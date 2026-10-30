# Planejamento experimental

**Estado: implementado** (backend). Transforma um protocolo cadastrado mais os
parâmetros do usuário num plano operacional pronto para execução na bancada.

Código: `backend/planejador/core/calculos.py` e
`backend/planejador/services/planejamento_service.py`.

## Cálculos disponíveis

Todas as funções são puras — recebem números, validam e devolvem resultado. Não
tocam banco nem interface, o que permite conferi-las contra cálculo manual.

| Função | O que faz | Base |
|---|---|---|
| `preparar_diluicao` | Volume de alíquota e de diluente para uma diluição simples | C₁·V₁ = C₂·V₂ |
| `diluicao_seriada` | Concentrações de uma série de diluições | Cᵢ = C₀ / fatorⁱ |
| `massa_de_soluto` | Massa necessária para uma concentração e volume | massa = concentração · volume |
| `escalonar_quantidade` | Total de um insumo para N reações, com margem de excesso | base · N · (1 + excesso/100) |
| `planejar_tubos` | Tubos de amostra, controle e preparo, e número de estantes | amostras · replicatas · pontos + controles · pontos + pontos |
| `planejar_microplaca` | Ocupação de poços e número de placas | amostras · replicatas · pontos + controles · pontos |

### Unidades

As funções são **agnósticas de unidade**: cabe a quem chama garantir coerência
(g/L com L dá g; mg/mL com mL dá mg). Essa decisão mantém o núcleo simples; a
unidade de cada reagente fica no banco, no campo `unidade`.

### Validação

Entradas inválidas levantam `EntradaInvalida`, com mensagem e dica de correção.
São rejeitados: valores ≤ 0 onde se espera positivo, fator de diluição ≤ 1,
concentração final maior que a inicial (não se concentra diluindo), contagens
menores que 1 e excesso percentual negativo.

## Geração do plano

`gerar_plano(session, protocolo_id, n_amostras, n_replicatas, n_controles, ...)`

1. Carrega o protocolo e seus vínculos de reagente e material.
2. Calcula o número de reações: `n_amostras · n_replicatas + n_controles`.
3. Escalona cada `quantidade_base` por esse número, aplicando o
   `excesso_percentual` (margem para perdas de pipetagem).
4. Calcula o **preparo da solução de trabalho**, se o usuário informou uma
   concentração final (ver abaixo).
5. Calcula quantos **tubos** e estantes o ensaio consome.
6. Se o protocolo for do tipo `microplaca`, calcula também a ocupação de poços.
7. Redige o **resumo do procedimento** a partir dos números já calculados — o
   texto nunca discorda do restante do plano.
8. Devolve um `PlanoOperacional` — dataclass com descrição do protocolo,
   reagentes, materiais, preparo, tubos, microplaca e procedimento, mais o
   método `como_dict()` para UI/JSON.

O plano não é persistido: é calculado sob demanda a partir do protocolo.

### Preparo da solução

A concentração final (`conc_final`) é o gatilho: sem ela, o plano não inclui a
seção de solução. Com ela, o cálculo segue um de dois caminhos:

| Situação | Entrada | Resultado |
|---|---|---|
| Há solução-mãe | `conc_inicial` informada | `preparar_diluicao` — volume de alíquota, de diluente e fator |
| Parte do sólido | `conc_inicial` ausente | `massa_de_soluto` — massa a pesar |

O volume total pode vir pronto (`volume_final`) ou ser derivado do consumo por
reação (`volume_por_reacao`), escalonado pelo número de reações com a mesma
margem de excesso aplicada aos reagentes. Informar `conc_final` sem nenhum dos
dois volumes levanta `EntradaInvalida`.

Passando `fator_serie` e `n_pontos_serie`, o plano inclui também a série de
diluição — e os pontos multiplicam a contagem de tubos.

## Protocolos são dados

Um protocolo é uma linha na tabela `protocolos` mais seus vínculos com
reagentes e materiais — não um módulo Python. Adicionar um protocolo novo não
exige alterar código, o que sustenta a expansão prevista para química e ensaios
biológicos.

O campo `tipo` (`preparo_solucao`, `diluicao`, `microplaca`...) é o que decide
quais cálculos se aplicam. Hoje há dois protocolos de exemplo semeados.

Ver [modelo de dados](../arquitetura/banco-de-dados.md) e
[protocolos](../protocolos/README.md).
