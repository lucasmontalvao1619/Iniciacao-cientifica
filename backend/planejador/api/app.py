"""API HTTP opcional que expõe os services (FastAPI).

Mantém a UI/integrações desacopladas do backend. Se o FastAPI não estiver
instalado, importar este módulo dá um erro claro explicando o extra necessário.

Os endpoints acompanham o fluxo do aplicativo de ponta a ponta:

    GET  /protocolos                          seleção do protocolo
    POST /planos                              plano operacional
    POST /experimentos                        registro do que foi executado
    POST /experimentos/{id}/medicoes          dados obtidos na bancada
    GET  /experimentos/{id}                   dados já tabulados
    GET  /experimentos/{id}/estatistica       análise estatística
    POST /experimentos/{id}/exportacoes       resultados em CSV
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from typing import Any

try:
    from fastapi import Depends, FastAPI, HTTPException, Query
    from pydantic import BaseModel, Field
except ModuleNotFoundError as exc:  # pragma: no cover - caminho opcional
    raise ModuleNotFoundError(
        "A API requer o extra 'api'. Instale com: pip install -e \".[api]\""
    ) from exc

from sqlalchemy.orm import Session

from ..bootstrap import iniciar
from ..core.exceptions import ErroPlanejamento, RegistroNaoEncontrado
from ..database import get_session
from ..services import (
    adicionar_medicoes,
    analisar_experimento,
    criar_experimento,
    exportar_experimento_csv,
    gerar_plano,
    listar_experimentos,
    listar_protocolos,
    obter_experimento,
)


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Garante banco pronto ao subir a API."""
    iniciar()
    yield


app = FastAPI(
    title="Planejador de Experimentos",
    version="0.2.0",
    lifespan=_lifespan,
)


def _sessao() -> Iterator[Session]:
    """Dependência de sessão por requisição."""
    with get_session() as session:
        yield session


def _tratar(erro: ErroPlanejamento) -> HTTPException:
    """Converte um erro de domínio na resposta HTTP correspondente.

    ``RegistroNaoEncontrado`` vira 404; qualquer outro erro de entrada vira 400
    com a ``dica`` de correção anexada, para a interface poder exibi-la ao lado
    do campo errado.
    """
    if isinstance(erro, RegistroNaoEncontrado):
        return HTTPException(status_code=404, detail=str(erro))
    detalhe: dict[str, Any] = {"mensagem": str(erro)}
    dica = getattr(erro, "dica", None)
    if dica:
        detalhe["dica"] = dica
    return HTTPException(status_code=400, detail=detalhe)


# --------------------------------------------------------------------------- #
# Protocolos
# --------------------------------------------------------------------------- #


@app.get("/protocolos")
def protocolos(sessao: Session = Depends(_sessao)) -> Any:
    """Lista os protocolos disponíveis para seleção."""
    return listar_protocolos(sessao)


# --------------------------------------------------------------------------- #
# Planejamento
# --------------------------------------------------------------------------- #


class PlanoRequest(BaseModel):
    """Corpo da requisição de geração de plano.

    Reúne as variáveis experimentais do fluxo: número de amostras, replicatas,
    controles, concentrações, volumes e série de diluição.
    """

    protocolo_id: int
    n_amostras: int = Field(ge=1)
    n_replicatas: int = Field(default=1, ge=1)
    n_controles: int = Field(default=0, ge=0)
    excesso_percentual: float = Field(default=0.0, ge=0)
    pocos_por_placa: int = Field(default=96, ge=1)
    tubos_por_rack: int = Field(default=24, ge=1)
    conc_inicial: float | None = Field(default=None, gt=0)
    conc_final: float | None = Field(default=None, gt=0)
    volume_final: float | None = Field(default=None, gt=0)
    volume_por_reacao: float | None = Field(default=None, gt=0)
    fator_serie: float | None = Field(default=None, gt=1)
    n_pontos_serie: int = Field(default=1, ge=1)


@app.post("/planos")
def criar_plano(req: PlanoRequest, sessao: Session = Depends(_sessao)) -> Any:
    """Gera um plano operacional a partir de um protocolo e parâmetros."""
    try:
        plano = gerar_plano(
            sessao,
            protocolo_id=req.protocolo_id,
            n_amostras=req.n_amostras,
            n_replicatas=req.n_replicatas,
            n_controles=req.n_controles,
            excesso_percentual=req.excesso_percentual,
            pocos_por_placa=req.pocos_por_placa,
            tubos_por_rack=req.tubos_por_rack,
            conc_inicial=req.conc_inicial,
            conc_final=req.conc_final,
            volume_final=req.volume_final,
            volume_por_reacao=req.volume_por_reacao,
            fator_serie=req.fator_serie,
            n_pontos_serie=req.n_pontos_serie,
        )
    except ErroPlanejamento as e:
        raise _tratar(e) from e
    return plano.como_dict()


# --------------------------------------------------------------------------- #
# Experimentos e medições
# --------------------------------------------------------------------------- #


class ExperimentoRequest(BaseModel):
    """Corpo da criação de um experimento, com medições opcionais."""

    protocolo_id: int
    titulo: str = Field(min_length=1)
    observacoes: str | None = None
    medicoes: dict[str, list[float]] | None = None


class MedicoesRequest(BaseModel):
    """Corpo do lançamento de medições em um experimento existente."""

    medicoes: dict[str, list[float]] = Field(
        description="Mapa {grupo: [valores...]}, ex.: {'controle': [1.0, 1.2]}"
    )


class ExportacaoRequest(BaseModel):
    """Corpo do pedido de exportação em CSV."""

    destino: str = Field(description="Diretório de saída dos arquivos CSV.")


@app.post("/experimentos", status_code=201)
def novo_experimento(
    req: ExperimentoRequest, sessao: Session = Depends(_sessao)
) -> Any:
    """Cria um experimento e, se enviadas, já registra suas medições."""
    try:
        return criar_experimento(
            sessao,
            protocolo_id=req.protocolo_id,
            titulo=req.titulo,
            observacoes=req.observacoes,
            medicoes=req.medicoes,
        )
    except ErroPlanejamento as e:
        raise _tratar(e) from e


@app.get("/experimentos")
def experimentos(
    protocolo_id: int | None = Query(default=None),
    sessao: Session = Depends(_sessao),
) -> Any:
    """Lista experimentos, opcionalmente filtrados por protocolo."""
    return listar_experimentos(sessao, protocolo_id)


@app.get("/experimentos/{experimento_id}")
def experimento(
    experimento_id: int, sessao: Session = Depends(_sessao)
) -> Any:
    """Devolve um experimento com as medições já organizadas em tabelas."""
    try:
        return obter_experimento(sessao, experimento_id)
    except ErroPlanejamento as e:
        raise _tratar(e) from e


@app.post("/experimentos/{experimento_id}/medicoes", status_code=201)
def novas_medicoes(
    experimento_id: int,
    req: MedicoesRequest,
    sessao: Session = Depends(_sessao),
) -> Any:
    """Acrescenta medições obtidas na bancada a um experimento."""
    try:
        return adicionar_medicoes(sessao, experimento_id, req.medicoes)
    except ErroPlanejamento as e:
        raise _tratar(e) from e


# --------------------------------------------------------------------------- #
# Análise e exportação
# --------------------------------------------------------------------------- #


@app.get("/experimentos/{experimento_id}/estatistica")
def estatistica_experimento(
    experimento_id: int,
    alpha: float = Query(default=0.05, gt=0, lt=1),
    sessao: Session = Depends(_sessao),
) -> Any:
    """Roda a análise estatística das medições de um experimento."""
    try:
        return analisar_experimento(sessao, experimento_id, alpha=alpha)
    except ErroPlanejamento as e:
        raise _tratar(e) from e


@app.post("/experimentos/{experimento_id}/exportacoes")
def exportar_experimento(
    experimento_id: int,
    req: ExportacaoRequest,
    sessao: Session = Depends(_sessao),
) -> Any:
    """Exporta as tabelas do experimento para arquivos CSV."""
    try:
        return exportar_experimento_csv(sessao, experimento_id, req.destino)
    except ErroPlanejamento as e:
        raise _tratar(e) from e
