"""Serviço de planejamento: transforma um protocolo + parâmetros em plano.

Combina os dados do banco (reagentes/materiais de um protocolo) com os cálculos
do núcleo (diluição, massa de soluto, escalonamento, tubos e microplaca) para
produzir o "plano operacional" que o usuário vê — exatamente a proposta central
do aplicativo.

O plano responde, de uma vez, às perguntas de bancada: quanto de cada reagente
pesar ou pipetar, como preparar a solução na concentração desejada, quantos
tubos e placas separar, e em que ordem executar.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from ..core import calculos
from ..core.exceptions import EntradaInvalida
from ..database import repositories


@dataclass(frozen=True)
class ItemPlano:
    """Um insumo do plano, já com a quantidade total calculada."""

    nome: str
    unidade: str
    quantidade_base: float
    quantidade_total: float


@dataclass(frozen=True)
class PreparoSolucao:
    """Como preparar a solução de trabalho do experimento.

    Preenchido de uma das duas formas, conforme o usuário informe ou não uma
    concentração inicial:

    * **Por diluição** (há solução-mãe): ``diluicao`` traz volume de alíquota,
      volume de diluente e fator de diluição.
    * **A partir do sólido** (não há solução-mãe): ``massa_soluto`` traz a massa
      a pesar para o volume e a concentração desejados.

    Attributes:
        conc_final: Concentração de trabalho desejada.
        volume_final: Volume total de solução a preparar.
        conc_inicial: Concentração da solução-mãe, se houver.
        diluicao: Resultado do cálculo C1·V1 = C2·V2, quando aplicável.
        massa_soluto: Massa a pesar, quando o preparo parte do sólido.
        serie_diluicao: Concentrações da série seriada, quando solicitada.
    """

    conc_final: float
    volume_final: float
    conc_inicial: float | None = None
    diluicao: calculos.ResultadoDiluicao | None = None
    massa_soluto: float | None = None
    serie_diluicao: list[float] | None = None

    def como_dict(self) -> dict:
        """Serializa o preparo para dict simples."""
        return {
            "conc_inicial": self.conc_inicial,
            "conc_final": self.conc_final,
            "volume_final": self.volume_final,
            "diluicao": vars(self.diluicao) if self.diluicao else None,
            "massa_soluto": self.massa_soluto,
            "serie_diluicao": self.serie_diluicao,
        }


@dataclass(frozen=True)
class PlanoOperacional:
    """Plano operacional gerado para um experimento.

    Attributes:
        protocolo: Nome do protocolo.
        tipo: Tipo do protocolo (ex.: ``microplaca``, ``preparo_solucao``).
        descricao: Descrição cadastrada do protocolo.
        n_amostras: Amostras planejadas.
        n_replicatas: Replicatas por amostra.
        n_controles: Controles planejados.
        n_reacoes: Total de reações (amostras × replicatas + controles).
        reagentes: Lista de reagentes com quantidades totais.
        materiais: Lista de materiais com quantidades totais.
        preparo: Preparo da solução de trabalho, se houver dados para calculá-lo.
        tubos: Contagem de tubos e estantes.
        microplaca: Organização em microplaca (poços e nº de placas).
        procedimento: Resumo do procedimento, passo a passo.
    """

    protocolo: str
    tipo: str
    n_amostras: int
    n_replicatas: int
    n_controles: int
    n_reacoes: int
    descricao: str | None = None
    reagentes: list[ItemPlano] = field(default_factory=list)
    materiais: list[ItemPlano] = field(default_factory=list)
    preparo: PreparoSolucao | None = None
    tubos: calculos.PlanoTubos | None = None
    microplaca: calculos.PlanoMicroplaca | None = None
    procedimento: list[str] = field(default_factory=list)

    def como_dict(self) -> dict:
        """Serializa o plano para dict simples (pronto para UI/JSON)."""
        return {
            "protocolo": self.protocolo,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "n_amostras": self.n_amostras,
            "n_replicatas": self.n_replicatas,
            "n_controles": self.n_controles,
            "n_reacoes": self.n_reacoes,
            "reagentes": [vars(i) for i in self.reagentes],
            "materiais": [vars(i) for i in self.materiais],
            "preparo": self.preparo.como_dict() if self.preparo else None,
            "tubos": vars(self.tubos) if self.tubos else None,
            "microplaca": vars(self.microplaca) if self.microplaca else None,
            "procedimento": list(self.procedimento),
        }


def _calcular_preparo(
    conc_final: float | None,
    volume_final: float | None,
    conc_inicial: float | None,
    volume_por_reacao: float | None,
    n_reacoes: int,
    excesso_percentual: float,
    fator_serie: float | None,
    n_pontos_serie: int,
) -> PreparoSolucao | None:
    """Calcula o preparo da solução, se o usuário informou dados suficientes.

    O volume final pode vir pronto (``volume_final``) ou ser derivado do volume
    consumido por reação, já escalonado para o número de reações e com a mesma
    margem de excesso aplicada aos reagentes.

    Returns:
        :class:`PreparoSolucao` ou ``None`` se não houver concentração alvo.

    Raises:
        EntradaInvalida: Se a concentração final foi informada sem nenhum
            volume, ou se algum valor for inconsistente.
    """
    if conc_final is None:
        return None

    if volume_final is None:
        if volume_por_reacao is None:
            raise EntradaInvalida(
                "Concentração final informada sem volume correspondente.",
                dica="Informe 'volume_final' ou 'volume_por_reacao'.",
            )
        volume_final = calculos.escalonar_quantidade(
            volume_por_reacao, n_reacoes, excesso_percentual
        )

    diluicao = None
    massa = None
    if conc_inicial is not None:
        diluicao = calculos.preparar_diluicao(
            conc_inicial, conc_final, volume_final
        )
    else:
        # Sem solução-mãe: o preparo parte do soluto sólido.
        massa = calculos.massa_de_soluto(conc_final, volume_final)

    serie = None
    if fator_serie is not None:
        serie = calculos.diluicao_seriada(conc_final, fator_serie, n_pontos_serie)

    return PreparoSolucao(
        conc_final=conc_final,
        volume_final=volume_final,
        conc_inicial=conc_inicial,
        diluicao=diluicao,
        massa_soluto=massa,
        serie_diluicao=serie,
    )


def _montar_procedimento(
    protocolo_nome: str,
    reagentes: list[ItemPlano],
    preparo: PreparoSolucao | None,
    tubos: calculos.PlanoTubos | None,
    microplaca: calculos.PlanoMicroplaca | None,
    n_amostras: int,
    n_replicatas: int,
    n_controles: int,
) -> list[str]:
    """Redige o resumo do procedimento em passos numeráveis.

    O texto é gerado a partir dos números já calculados, para que o resumo
    nunca discorde do restante do plano.
    """
    passos: list[str] = [f"Separar o material do protocolo '{protocolo_nome}'."]

    if reagentes:
        itens = ", ".join(
            f"{r.nome}: {r.quantidade_total:.4g} {r.unidade}" for r in reagentes
        )
        passos.append(f"Pesar/medir os reagentes — {itens}.")

    if preparo is not None:
        if preparo.diluicao is not None:
            d = preparo.diluicao
            passos.append(
                f"Preparar a solução de trabalho: retirar {d.volume_alicota:.4g} "
                f"da solução-mãe ({preparo.conc_inicial:.4g}) e completar com "
                f"{d.volume_diluente:.4g} de diluente até {d.volume_final:.4g} "
                f"(fator {d.fator_diluicao:.4g}×, concentração final "
                f"{preparo.conc_final:.4g})."
            )
        elif preparo.massa_soluto is not None:
            passos.append(
                f"Preparar a solução de trabalho: pesar "
                f"{preparo.massa_soluto:.4g} de soluto e completar até "
                f"{preparo.volume_final:.4g} para obter "
                f"{preparo.conc_final:.4g}."
            )
        if preparo.serie_diluicao:
            pontos = ", ".join(f"{c:.4g}" for c in preparo.serie_diluicao)
            passos.append(f"Montar a série de diluição nos pontos: {pontos}.")

    if tubos is not None:
        passos.append(
            f"Identificar {tubos.tubos_totais} tubos "
            f"({tubos.tubos_amostras} de amostra, {tubos.tubos_controles} de "
            f"controle, {tubos.tubos_preparo} de preparo) em "
            f"{tubos.racks_necessarios} estante(s)."
        )

    if microplaca is not None:
        passos.append(
            f"Distribuir em {microplaca.placas_necessarias} microplaca(s) de "
            f"{microplaca.pocos_por_placa} poços, ocupando "
            f"{microplaca.pocos_totais} poços "
            f"({microplaca.pocos_amostras} de amostra, "
            f"{microplaca.pocos_controles} de controle)."
        )

    passos.append(
        f"Executar o ensaio com {n_amostras} amostra(s) em "
        f"{n_replicatas} replicata(s) e {n_controles} controle(s)."
    )
    passos.append(
        "Registrar as medições no aplicativo para a análise estatística."
    )
    return passos


def gerar_plano(
    session: Session,
    protocolo_id: int,
    n_amostras: int,
    n_replicatas: int = 1,
    n_controles: int = 0,
    *,
    excesso_percentual: float = 0.0,
    pocos_por_placa: int = 96,
    tubos_por_rack: int = 24,
    conc_inicial: float | None = None,
    conc_final: float | None = None,
    volume_final: float | None = None,
    volume_por_reacao: float | None = None,
    fator_serie: float | None = None,
    n_pontos_serie: int = 1,
) -> PlanoOperacional:
    """Gera o plano operacional de um experimento.

    Args:
        session: Sessão do banco.
        protocolo_id: Protocolo escolhido pelo usuário.
        n_amostras: Número de amostras.
        n_replicatas: Replicatas por amostra.
        n_controles: Poços/tubos de controle.
        excesso_percentual: Margem de segurança aplicada às quantidades.
        pocos_por_placa: Capacidade da microplaca (se aplicável).
        tubos_por_rack: Capacidade da estante de tubos.
        conc_inicial: Concentração da solução-mãe, se o preparo for por diluição.
        conc_final: Concentração de trabalho desejada. É o gatilho do cálculo de
            preparo: sem ela, o plano não inclui a seção de solução.
        volume_final: Volume total de solução a preparar.
        volume_por_reacao: Alternativa a ``volume_final`` — volume gasto por
            reação, escalonado internamente pelo número de reações.
        fator_serie: Fator entre pontos de uma diluição seriada (ex.: 10).
        n_pontos_serie: Número de pontos da série (também multiplica os tubos).

    Returns:
        :class:`PlanoOperacional` completo.

    Raises:
        RegistroNaoEncontrado: Se o protocolo não existir.
        EntradaInvalida: Se os parâmetros forem inconsistentes.
    """
    protocolo = repositories.obter_protocolo(session, protocolo_id)

    # nº total de reações = amostras × replicatas + controles
    n_reacoes = n_amostras * n_replicatas + n_controles

    reagentes: list[ItemPlano] = []
    for vinc in protocolo.reagentes:
        total = calculos.escalonar_quantidade(
            float(vinc.quantidade_base), n_reacoes, excesso_percentual
        )
        reagentes.append(
            ItemPlano(
                nome=vinc.reagente.nome,
                unidade=vinc.reagente.unidade,
                quantidade_base=float(vinc.quantidade_base),
                quantidade_total=total,
            )
        )

    materiais: list[ItemPlano] = []
    for vinc_m in protocolo.materiais:
        total_m = calculos.escalonar_quantidade(
            float(vinc_m.quantidade_base), n_reacoes, excesso_percentual
        )
        materiais.append(
            ItemPlano(
                nome=vinc_m.material.nome,
                unidade=vinc_m.material.tipo or "un",
                quantidade_base=float(vinc_m.quantidade_base),
                quantidade_total=total_m,
            )
        )

    preparo = _calcular_preparo(
        conc_final=conc_final,
        volume_final=volume_final,
        conc_inicial=conc_inicial,
        volume_por_reacao=volume_por_reacao,
        n_reacoes=n_reacoes,
        excesso_percentual=excesso_percentual,
        fator_serie=fator_serie,
        n_pontos_serie=n_pontos_serie,
    )

    tubos = calculos.planejar_tubos(
        n_amostras,
        n_replicatas,
        n_controles,
        n_pontos_diluicao=n_pontos_serie,
        tubos_por_rack=tubos_por_rack,
    )

    microplaca = None
    if protocolo.tipo == "microplaca":
        microplaca = calculos.planejar_microplaca(
            n_amostras,
            n_replicatas,
            n_controles,
            n_pontos_diluicao=n_pontos_serie,
            pocos_por_placa=pocos_por_placa,
        )

    return PlanoOperacional(
        protocolo=protocolo.nome,
        tipo=protocolo.tipo,
        descricao=protocolo.descricao,
        n_amostras=n_amostras,
        n_replicatas=n_replicatas,
        n_controles=n_controles,
        n_reacoes=n_reacoes,
        reagentes=reagentes,
        materiais=materiais,
        preparo=preparo,
        tubos=tubos,
        microplaca=microplaca,
        procedimento=_montar_procedimento(
            protocolo.nome,
            reagentes,
            preparo,
            tubos,
            microplaca,
            n_amostras,
            n_replicatas,
            n_controles,
        ),
    )
