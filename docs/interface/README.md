# Interface do planejamento experimental

Código ativo: `~/Desktop/INICIACAO CIENTIFICA`. Executar com `.venv/bin/python -m frontend.app`; dependências de UI: `pip install -e ".[ui]"`.

## Estado em 08/11/2026

- Dez itens no catálogo: PREP-001 a PREP-010. PREP-001 tem cálculo percentual e PREP-002 tem cálculo molar; PREP-003 tem cálculo de estoque; PREP-004 tem diluição de solução-estoque; PREP-005 tem diluição seriada; PREP-006 calcula fator/concentração final; PREP-007 calcula volume total e excedente; PREP-008 escala formulações; PREP-009 calcula meio comercial pela instrução declarada; PREP-010 está em implantação e não geram resultados fictícios.
- Protocolo: pesquisa integrada ao dropdown; X limpa seleção, descrição e estado dependente. Ver POP e gerar DOCX usam dados do item selecionado. PREP-001 a PREP-003 incluem fontes integrais consultadas e foto ilustrativa creditada. Fichas dos demais mostram suas pendências.
- Parâmetros: PREP-001 usa base percentual, concentração, quantidade final, teor/pureza, soluto e solvente. Sem amostras/replicatas/controles genéricos que não se aplicam ao preparo.
- Parâmetros de PREP-002: mol/L, volume final em mL, massa molar, teor % m/m, soluto/solvente e forma de medir. Densidade do reagente comercial é solicitada somente para líquido medido por volume.
- Plano: quantidade calculada de reagente comercial, solvente q.s.p. ou massa de solvente, procedimento geral, fonte e limites de aplicação.
- Resultados: os mesmos parâmetros podem ser editados com recálculo e gráfico ao vivo. O gráfico é de dimensionamento, sem representar medições ou teste estatístico. Entradas inválidas removem o resultado exportável até correção.
- Início: histórico persistente de até dez experimentos. Itens excedentes ou retirados são arquivados em `Registros de Experimentos`, para consulta e exportação somente, conforme escolha de Lucas. A consulta não reabre a sessão.

## Persistência e distribuição

O histórico fica em SQLite nos dados locais do usuário; `PLANEJADOR_DATA_DIR` permite isolamento de teste. No aplicativo portátil empacotado, os arquivos arquivados usam a pasta ao lado do executável/bundle. Se não houver permissão de escrita, o app usa os dados do usuário e exibe o caminho real na tela inicial. O ZIP Windows preparado inclui a pasta.

Planejamentos calculados e ajustes válidos em Resultados atualizam o mesmo registro. Um novo planejamento/protocolo gera outro registro. A remoção grava o arquivo antes de retirar a linha do histórico; falha de gravação preserva a linha. JSON guarda parâmetros, plano e fontes; dados observados só aparecem quando efetivamente registrados pelo módulo estatístico existente.

## Limites e verificações

As definições e técnica geral vêm da Fiocruz, 2009, p. 226–232 e 249–250. A obra é candidata compatível com o recorte confirmado; o registro Arca ainda não foi localizado e a fonte não foi contabilizada como incluída na revisão. Não há validação em bancada.

Abertura mantém estatística/gráficos carregados sob demanda. Windows é prioridade; a receita de compilação foi preparada, mas Lucas informou não ter Windows disponível agora para teste. Ver `../distribuicao/README.md` e `../modulos/IMPLEMENTACAO_PREP.md`.

## Perguntas variáveis em 08/11/2026

PREP-001 a PREP-003 apresentam os parâmetros como perguntas condicionais. Campos numéricos começam sem resposta; identidade de substância/solvente é opcional para o cálculo. No estoque, identificação e conservação ficam em grupo opcional e pendências são preservadas. Conversão entre atividade e massa exige equivalência específica fornecida pelo pesquisador. 165 testes passaram na suíte completa; Ruff sem erros. Capturas Qt dos parâmetros e do gráfico conferidas; janela de 880 px com identificação expandida sem rolagem horizontal ou corte do texto explicativo. POP de PREP-003 conferido em três páginas. Pacote Mac PREP-001-a-003 gerado; Windows ainda não testado.

## PREP-004 em 08/11/2026

Perguntas: concentração do estoque, concentração desejada, unidade comum por volume e volume final em mL. Identificação do estoque/diluente é opcional. Sem teor, massa molar, dados de frasco ou replicatas desnecessários. O plano mostra alíquota e fator; diluente q.s.p., sem apresentar a diferença de volumes como dosagem exata. Resultados permite editar as perguntas com recálculo e gráfico de dimensionamento. 181 testes da suíte completa passaram; fonte Fiocruz p. 232, consulta e imagem registradas, DOCX conferido em duas páginas.

## PREP-005 em 08/11/2026

Série com perguntas de C0/unidade, fator, número de diluições excluindo estoque, volume preparado antes da próxima transferência e retirada opcional no último recipiente. Plano e Resultados mostram tabela de concentrações, fator acumulado, alíquota, diluente nominal e volume restante. Gráfico logarítmico inclui estoque na etapa 0, com etapas inteiras; edição atualiza tabela, gráfico e mesmo registro de histórico. Valores inválidos removem resultado/gráfico exportável. 202 testes passaram e DOCX de três páginas/capturas Qt foram conferidos. Fontes e discrepância bibliográfica em REGISTRO.md.

## PREP-006 em 08/11/2026

Perguntas de concentração inicial, unidade por volume, alíquota e volume final. Fator e concentração final são saídas. Nomes opcionais; sem campos de pureza/massa molar. Resultados edita as três grandezas e recalcula curva de concentração final por volume final, mantendo estoque e alíquota fixos; ponto marca o preparo. Histórico/JSON preservam dados e fontes. 219 testes passaram; capturas Qt e duas páginas do POP ilustrado conferidas, página de 880 px sem rolagem horizontal. Fonte e data/hora em REGISTRO.md.

## PREP-007 em 08/11/2026

Volume por unidade, contagem total de unidades, percentual a acrescentar e unidade (µL/mL/L) perguntados. Identificação do material opcional, sem concentração/pureza/solvente desnecessários. Plano e Resultados mostram base, reserva e total, com gráfico comparativo editável; zero representa sem reserva. Histórico e JSON atualizados. 237 testes passaram; POP ilustrado de duas páginas e capturas Qt conferidos. BVS MS, Guia 2016 p. 48, obtenção/consulta e nova imagem registrados em REGISTRO.md.

## PREP-008 em 08/11/2026

Formulação em painel próprio carregado ao selecionar o protocolo: referência Anvisa protegida e receita do pesquisador separada. Volume nominal, ingredientes/unidades e condições variáveis são perguntas; ciclo desconhecido fica pendente. A referência mostra pH/conservação da fonte e não calcula validade. Resultados mostra quantidades de todos os componentes e permite escolher um no gráfico; edição atualiza cálculo, tabela e mesmo registro de histórico. Receita livre preserva fonte/autoria declarada, sem validar automaticamente a composição. 251 testes passaram; capturas e DOCX de duas páginas conferidos, fonte e consultas em REGISTRO.md.

## PREP-009 em 08/11/2026

Painel de meio comercial carregado ao selecionar o protocolo. Perguntas para massa/volume de referência, volume alvo e convenção água/final, sem presumir respostas. Rótulo/documento/versão declarados pelo pesquisador; produto opcional, condições desconhecidas pendentes. Resultados recalcula massa e gráfico, com eixo de volume coerente com a escolha. Histórico/JSON preservam a fonte declarada e a fonte técnica separadas. 265 testes passaram; capturas Qt e POP ilustrado de duas páginas conferidos.
