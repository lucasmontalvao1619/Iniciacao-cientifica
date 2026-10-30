"""Cálculos operacionais de laboratório.

Funções puras: recebem números, validam e devolvem resultados. Não acessam
banco, UI nem imprimem nada — o que as torna simples de testar contra cálculos
manuais conferidos (etapa de validação técnica do projeto).

Convenção de unidades: as funções são agnósticas de unidade, desde que a
entrada seja coerente (mesma base). Cabe à camada superior garantir unidades.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .exceptions import EntradaInvalida


def _exigir_positivo(nome: str, valor: float) -> None:
    """Valida que ``valor`` é estritamente positivo."""
    if valor <= 0:
        raise EntradaInvalida(
            f"O valor de '{nome}' deve ser positivo (recebido: {valor}).",
            dica="Verifique se não digitou zero ou um número negativo.",
        )


@dataclass(frozen=True)
class ResultadoDiluicao:
    """Resultado do preparo de uma diluição simples.

    Attributes:
        volume_alicota: Volume da solução-mãe a ser retirado.
        volume_diluente: Volume de diluente a acrescentar.
        volume_final: Volume total da solução preparada.
        fator_diluicao: Razão entre concentração inicial e final.
    """

    volume_alicota: float
    volume_diluente: float
    volume_final: float
    fator_diluicao: float


def preparar_diluicao(
    conc_inicial: float, conc_final: float, volume_final: float
) -> ResultadoDiluicao:
    """Calcula uma diluição simples pela relação C1·V1 = C2·V2.

    Args:
        conc_inicial: Concentração da solução-mãe (C1).
        conc_final: Concentração desejada após diluir (C2).
        volume_final: Volume final desejado (V2).

    Returns:
        :class:`ResultadoDiluicao` com volume de alíquota e de diluente.

    Raises:
        EntradaInvalida: Se algum valor for <= 0 ou se ``conc_final`` for maior
            que ``conc_inicial`` (não é possível concentrar diluindo).

    Example:
        >>> r = preparar_diluicao(10.0, 1.0, 100.0)
        >>> r.volume_alicota, r.volume_diluente
        (10.0, 90.0)
    """
    _exigir_positivo("conc_inicial", conc_inicial)
    _exigir_positivo("conc_final", conc_final)
    _exigir_positivo("volume_final", volume_final)
    if conc_final > conc_inicial:
        raise EntradaInvalida(
            f"Concentração final ({conc_final}) maior que a inicial "
            f"({conc_inicial}).",
            dica="Diluir só reduz a concentração; verifique se inverteu os valores.",
        )
    volume_alicota = conc_final * volume_final / conc_inicial
    volume_diluente = volume_final - volume_alicota
    return ResultadoDiluicao(
        volume_alicota=volume_alicota,
        volume_diluente=volume_diluente,
        volume_final=volume_final,
        fator_diluicao=conc_inicial / conc_final,
    )


def diluicao_seriada(
    conc_inicial: float, fator: float, n_pontos: int
) -> list[float]:
    """Gera as concentrações de uma diluição seriada.

    Args:
        conc_inicial: Concentração do primeiro ponto.
        fator: Fator de diluição entre pontos consecutivos (ex.: 2 ou 10).
        n_pontos: Número total de pontos (incluindo o inicial).

    Returns:
        Lista de concentrações, do mais concentrado ao mais diluído.

    Raises:
        EntradaInvalida: Se ``conc_inicial`` <= 0, ``fator`` <= 1 ou
            ``n_pontos`` < 1.

    Example:
        >>> diluicao_seriada(100.0, 10.0, 4)
        [100.0, 10.0, 1.0, 0.1]
    """
    _exigir_positivo("conc_inicial", conc_inicial)
    if fator <= 1:
        raise EntradaInvalida(
            f"O fator de diluição deve ser maior que 1 (recebido: {fator}).",
            dica="Um fator 10 significa diluir 1:10 a cada ponto.",
        )
    if n_pontos < 1:
        raise EntradaInvalida("O número de pontos deve ser ao menos 1.")
    return [conc_inicial / (fator**i) for i in range(n_pontos)]


def massa_de_soluto(concentracao: float, volume: float) -> float:
    """Calcula a massa de soluto para uma dada concentração e volume.

    Usa a relação massa = concentração · volume. As unidades devem ser
    coerentes (ex.: g/L e L → g; mg/mL e mL → mg).

    Args:
        concentracao: Concentração desejada (massa por volume).
        volume: Volume final da solução.

    Returns:
        Massa de soluto necessária.

    Raises:
        EntradaInvalida: Se algum valor for <= 0.

    Example:
        >>> massa_de_soluto(9.0, 1.0)   # 9 g/L em 1 L
        9.0
    """
    _exigir_positivo("concentracao", concentracao)
    _exigir_positivo("volume", volume)
    return concentracao * volume


def escalonar_quantidade(
    quantidade_base: float, n_reacoes: int, excesso_percentual: float = 0.0
) -> float:
    """Escalona uma quantidade base para várias reações, com excesso opcional.

    Útil para calcular o total de um reagente para N amostras, prevendo uma
    margem de segurança (ex.: 10% de excesso para perdas de pipetagem).

    Args:
        quantidade_base: Quantidade para uma única reação/amostra.
        n_reacoes: Número de reações/amostras.
        excesso_percentual: Margem extra, em porcentagem (ex.: 10 para 10%).

    Returns:
        Quantidade total necessária.

    Raises:
        EntradaInvalida: Se ``quantidade_base`` <= 0, ``n_reacoes`` < 1 ou
            ``excesso_percentual`` < 0.

    Example:
        >>> escalonar_quantidade(2.0, 10, 10.0)
        22.0
    """
    _exigir_positivo("quantidade_base", quantidade_base)
    if n_reacoes < 1:
        raise EntradaInvalida("O número de reações deve ser ao menos 1.")
    if excesso_percentual < 0:
        raise EntradaInvalida("O excesso percentual não pode ser negativo.")
    return quantidade_base * n_reacoes * (1 + excesso_percentual / 100)


@dataclass(frozen=True)
class PlanoMicroplaca:
    """Organização de um ensaio em microplacas.

    Attributes:
        pocos_amostras: Poços ocupados por amostras × replicatas × pontos.
        pocos_controles: Poços ocupados por controles, em todos os pontos.
        pocos_totais: Total de poços utilizados.
        placas_necessarias: Número de placas necessárias.
        pocos_por_placa: Capacidade de cada placa considerada.
        n_pontos_diluicao: Pontos da série considerados no cálculo.
    """

    pocos_amostras: int
    pocos_controles: int
    pocos_totais: int
    placas_necessarias: int
    pocos_por_placa: int
    n_pontos_diluicao: int = 1


def planejar_microplaca(
    n_amostras: int,
    n_replicatas: int,
    n_controles: int = 0,
    n_pontos_diluicao: int = 1,
    pocos_por_placa: int = 96,
) -> PlanoMicroplaca:
    """Calcula a ocupação de poços e o número de microplacas necessárias.

    Cada amostra ocupa um poço por replicata **e por ponto de diluição** — num
    ensaio de dose-resposta com 4 concentrações, uma amostra em triplicata usa
    12 poços. Os controles também são contados uma vez por ponto, seguindo a
    mesma convenção de :func:`planejar_tubos`.

    Diferente dos tubos, não há poço de preparo: as diluições são preparadas em
    tubo e só as alíquotas finais vão para a placa.

    Args:
        n_amostras: Número de amostras distintas.
        n_replicatas: Replicatas por amostra.
        n_controles: Controles por ponto de diluição.
        n_pontos_diluicao: Pontos da série de diluição (1 = sem série).
        pocos_por_placa: Capacidade da placa (padrão 96).

    Returns:
        :class:`PlanoMicroplaca` com contagens e número de placas.

    Raises:
        EntradaInvalida: Se ``n_amostras`` < 1, ``n_replicatas`` < 1,
            ``n_controles`` < 0, ``n_pontos_diluicao`` < 1 ou
            ``pocos_por_placa`` < 1.

    Example:
        >>> p = planejar_microplaca(8, 3, 2)
        >>> p.pocos_totais, p.placas_necessarias
        (26, 1)

        Com uma série de 3 pontos, o mesmo ensaio triplica a ocupação:

        >>> p = planejar_microplaca(8, 3, 2, n_pontos_diluicao=3)
        >>> p.pocos_amostras, p.pocos_totais, p.placas_necessarias
        (72, 78, 1)
    """
    if n_amostras < 1:
        raise EntradaInvalida("É necessário ao menos 1 amostra.")
    if n_replicatas < 1:
        raise EntradaInvalida("É necessário ao menos 1 replicata.")
    if n_controles < 0:
        raise EntradaInvalida("O número de controles não pode ser negativo.")
    if n_pontos_diluicao < 1:
        raise EntradaInvalida(
            "A série de diluição deve ter ao menos 1 ponto.",
            dica="Use 1 quando não houver diluição seriada.",
        )
    if pocos_por_placa < 1:
        raise EntradaInvalida("A placa deve ter ao menos 1 poço.")
    pocos_amostras = n_amostras * n_replicatas * n_pontos_diluicao
    pocos_controles = n_controles * n_pontos_diluicao
    pocos_totais = pocos_amostras + pocos_controles
    placas = math.ceil(pocos_totais / pocos_por_placa)
    return PlanoMicroplaca(
        pocos_amostras=pocos_amostras,
        pocos_controles=pocos_controles,
        pocos_totais=pocos_totais,
        placas_necessarias=placas,
        pocos_por_placa=pocos_por_placa,
        n_pontos_diluicao=n_pontos_diluicao,
    )


@dataclass(frozen=True)
class PlanoTubos:
    """Contagem de tubos necessários para um ensaio.

    Attributes:
        tubos_amostras: Tubos ocupados por amostras × replicatas.
        tubos_controles: Tubos reservados a controles.
        tubos_preparo: Tubos de preparo (solução-mãe, diluições intermediárias).
        tubos_totais: Soma de todos os tubos.
        tubos_por_rack: Capacidade da estante considerada.
        racks_necessarios: Estantes necessárias para acomodar os tubos.
    """

    tubos_amostras: int
    tubos_controles: int
    tubos_preparo: int
    tubos_totais: int
    tubos_por_rack: int
    racks_necessarios: int


def planejar_tubos(
    n_amostras: int,
    n_replicatas: int = 1,
    n_controles: int = 0,
    n_pontos_diluicao: int = 1,
    tubos_por_rack: int = 24,
) -> PlanoTubos:
    """Calcula quantos tubos o experimento consome.

    Cada amostra ocupa um tubo por replicata e por ponto de diluição — numa
    diluição seriada de 4 pontos, uma amostra em triplicata usa 12 tubos. Os
    controles são contados uma vez por ponto de diluição, e reserva-se um tubo
    de preparo por ponto (solução-mãe e diluições intermediárias).

    Args:
        n_amostras: Número de amostras distintas.
        n_replicatas: Replicatas por amostra.
        n_controles: Tubos de controle por ponto de diluição.
        n_pontos_diluicao: Pontos da série de diluição (1 = sem série).
        tubos_por_rack: Capacidade da estante de tubos (padrão 24).

    Returns:
        :class:`PlanoTubos` com as contagens e o número de estantes.

    Raises:
        EntradaInvalida: Se ``n_amostras`` < 1, ``n_replicatas`` < 1,
            ``n_controles`` < 0, ``n_pontos_diluicao`` < 1 ou
            ``tubos_por_rack`` < 1.

    Example:
        >>> t = planejar_tubos(8, 3, 2)
        >>> t.tubos_amostras, t.tubos_totais
        (24, 27)
    """
    if n_amostras < 1:
        raise EntradaInvalida("É necessário ao menos 1 amostra.")
    if n_replicatas < 1:
        raise EntradaInvalida("É necessário ao menos 1 replicata.")
    if n_controles < 0:
        raise EntradaInvalida("O número de controles não pode ser negativo.")
    if n_pontos_diluicao < 1:
        raise EntradaInvalida(
            "A série de diluição deve ter ao menos 1 ponto.",
            dica="Use 1 quando não houver diluição seriada.",
        )
    if tubos_por_rack < 1:
        raise EntradaInvalida("A estante deve comportar ao menos 1 tubo.")

    tubos_amostras = n_amostras * n_replicatas * n_pontos_diluicao
    tubos_controles = n_controles * n_pontos_diluicao
    tubos_preparo = n_pontos_diluicao
    tubos_totais = tubos_amostras + tubos_controles + tubos_preparo
    return PlanoTubos(
        tubos_amostras=tubos_amostras,
        tubos_controles=tubos_controles,
        tubos_preparo=tubos_preparo,
        tubos_totais=tubos_totais,
        tubos_por_rack=tubos_por_rack,
        racks_necessarios=math.ceil(tubos_totais / tubos_por_rack),
    )
