# Análise estatística

**Estado em 08/11/2026:** backend e interface integrados aos dez PREP. Resultados reúne dimensionamento editável e uma seção recolhível de medições observadas, sem preencher medições a partir do planejamento.

Código: `backend/planejador/core/estatistica.py`, `core/tabelas.py` e
`backend/planejador/services/estatistica_service.py`. Usa NumPy, SciPy e Pandas.

## Estatística descritiva

| Função | Devolve |
|---|---|
| `media` | Média aritmética |
| `desvio_padrao` | Desvio padrão (amostral por padrão; `amostral=False` para populacional) |
| `variancia` | Variância (mesma convenção) |
| `erro_padrao` | Erro padrão da média |
| `resumo` | `ResumoDescritivo` com n, média, desvio, variância, erro padrão, mínimo e máximo |

O padrão **amostral** (denominador n−1) é o correto para dados experimentais,
onde as medições são uma amostra e não a população inteira.

## Testes de hipótese

### Teste t — `teste_t(grupo_a, grupo_b, welch=False, alpha=0.05)`

Teste t de Student para **duas amostras independentes**. Com `welch=True`, usa a
correção de Welch, que não assume variâncias iguais entre os grupos.

Devolve `ResultadoTesteT`: estatística t, valor-p, graus de liberdade, o `alpha`
usado e `significativo` (verdadeiro quando p < alpha).

Exige ao menos 2 valores por grupo.

### ANOVA — `anova_uma_via(*grupos, alpha=0.05)`

ANOVA de uma via, para comparar **três ou mais grupos**. Devolve
`ResultadoAnova`: estatística F, valor-p, número de grupos e `significativo`.

Aceita 2 grupos tecnicamente, mas nesse caso a mensagem de erro sugere o teste t.
Exige ao menos 2 valores por grupo.

> A ANOVA indica que **existe** diferença entre os grupos, não **quais** grupos
> diferem. Teste post-hoc (Tukey) não está implementado.

## Escolha automática do teste

`analisar_grupos({"controle": [...], "tratamento": [...]})` calcula o resumo de
cada grupo e escolhe o teste pelo número de grupos:

| Grupos | Teste aplicado |
|---|---|
| 1 | Apenas resumo descritivo |
| 2 | Teste t |
| 3 ou mais | ANOVA de uma via |

Devolve um dicionário com `resumos`, as tabelas estruturadas
(`tabela_medicoes` e `tabela_resumo`) e `teste_t`/`anova` (nulos quando não se
aplicam).

`analisar_experimento(session, experimento_id)` faz o mesmo, mas lendo as
medições salvas no banco, agrupadas pelo campo `grupo` da tabela `medicoes`.

## Organização em tabelas

`core/tabelas.py` transforma o mapa `{grupo: [valores...]}` em `DataFrame`:

| Função | Devolve |
|---|---|
| `tabela_medicoes` | Dados brutos em formato longo: `grupo`, `replicata`, `valor` |
| `tabela_resumo` | Uma linha por grupo: n, média, desvio, variância, erro padrão, CV%, mínimo e máximo |
| `tabela_insumos` | Reagentes/materiais de um plano com quantidade base e total |
| `para_registros` | Converte a tabela em `list[dict]` serializável (NaN/inf viram `None`) |
| `exportar_csv` | Grava a tabela em CSV com `;` e vírgula decimal (Excel em português) |

O **coeficiente de variação** (CV%) é o acréscimo em relação ao `resumo` do
módulo de estatística: é o número que se olha em bancada para julgar a
repetibilidade entre replicatas. Grupos com uma única medição não têm dispersão
definida e recebem `NaN` nessas colunas, em vez de erro.

`exportar_experimento_csv(session, experimento_id, destino)` grava os dois
arquivos (`_medicoes.csv` e `_resumo.csv`) de uma vez.

## Nível de significância

`alpha` é 0,05 por padrão e é parâmetro em todas as funções de teste. O valor
usado volta no resultado, para que o relatório registre sob qual critério a
decisão foi tomada.

## Interface e persistência dos dez PREP em 08/11/2026

Em Resultados, expandir “Medições observadas e análise estatística”. O pesquisador informa nomes de grupos, valores separados por ponto e vírgula e grandeza/unidade. O caminho padrão calcula média, desvio padrão e variância amostrais, com pelo menos dois valores por grupo, e desenha os pontos observados. A comparação é opcional, nas opções avançadas; os pressupostos e a independência continuam sob avaliação do pesquisador. Não há teste pareado, pós-teste ou verificação automática de pressupostos.

O plano permanece separado das observações. Navegar entre Plano e Resultados preserva as medições; editar parâmetros do planejamento limpa o contexto e a análise anteriores. Valores não numéricos/não finitos são recusados na análise. Resultados estatísticos indefinidos ou fora da faixa não são exportados como NaN/Infinity; o rascunho continua disponível para correção.

O histórico SQLite guarda no mesmo registro o planejamento e `resultados_observados`: linhas digitadas, unidade, opções, estado `rascunho` ou `analisado` e, quando válida, análise e medições numéricas. As edições são gravadas após 400 ms; fechar, trocar protocolo ou arquivar descarrega a gravação pendente. Falha de gravação conserva uma cópia independente em memória; essas ações ficam bloqueadas até salvar ou exportar uma cópia de consulta pelo Início. A cópia preserva o plano e as medições mesmo se os parâmetros da tela forem invalidados depois da falha. Cancelar ou falhar na exportação mantém os dados pendentes; exportar com sucesso preserva o arquivo escolhido sem afirmar atualização do histórico. Encerramento forçado do processo continua sem garantia para dados mantidos apenas em memória. Rascunhos incompletos são preservados como texto, sem serem apresentados como resultados analisados. Arquivos excedentes/retirados e a consulta do histórico preservam observações para consulta e exportação, sem reabrir sessões. O JSON do experimento agrega plano e observações; o PNG contém o gráfico dos dados observados.

Verificação: 292 testes passaram na suíte completa; 12 testes de integração repetidos após ampliar as verificações de gravação temporizada e arquivamento imediato. Casos incluem todos os dez protocolos, média 4/desvio 2/variância 4 para [2,4,6], vínculo de protocolo, edição e invalidação, histórico, fechamento/reinício, rascunho inválido, consulta/arquivo e estatística indefinida. Ruff aprovado. Um aviso preexistente Starlette/httpx e um aviso SciPy esperado no caso degenerado; a interface recusa a análise indefinida. Capturas Qt e gráfico inspecionados em 880 px, corrigindo rolagem horizontal e cabeçalhos cortados. Não houve leitor de tela, cliques no novo bundle ou teste Windows. Gráficos futuros continuam fora desta entrega; RF16 agora tem o gráfico de pontos observado e gráficos de dimensionamento.

## Primeira interface (30/10/2026)

`frontend/analysis.py` apresenta resumos e comparação opcional dos services, além de gráfico de pontos Matplotlib e exportação PNG. A primeira entrega cobre gráfico de pontos por grupo, não todas as visualizações futuras. Entrada em memória, sem gravação automática das medições no banco.


Verificação da proteção de gravação: defeito reproduzido antes da correção (fechamento permitido após falha simulada); 295 testes passaram na suíte completa. Três testes de falha/recuperação repetidos após o ajuste que torna o botão de exportação visível. Cobrem tentativa automática, bloqueios, recuperação do histórico, cópia após invalidação do plano, cancelamento/erro de exportação e falha de atualização da lista depois da gravação efetiva. Captura `falha-gravacao-recuperacao-880.png` inspecionada, ação visível sem rolagem horizontal.


## Resultados simplificados — versão 0.2.5 (08/11/2026)

O resumo das quantidades calculadas abre antes do formulário. Ajustar planejamento, simulação gráfica e medições são expansões; Matplotlib e canvas só são construídos ao solicitar gráfico/análise. A troca de componente ou expansão da simulação, sem mudar parâmetros/plano, não grava o histórico nem limpa medições.

Medições: uma linha por grupo, uma coluna por valor. Colar do Excel (botão ou atalho de colar na tabela, inclusive durante edição) aceita retângulos separados por tabulações, sem cabeçalho, com grupo na primeira coluna e valores nas seguintes. Pode colar parcialmente a partir da célula atual e acrescentar medições/grupos. Limite de 10.000 células por colagem; inválidos ficam preservados no rascunho e são recusados pela análise. Entradas anteriores com listas separadas por ponto e vírgula continuam aceitas.

O botão Ver resumo e gráfico executa a estatística em tarefa de fundo; widgets e desenho permanecem na thread principal. Se dados, contexto ou opções mudarem durante o cálculo, seu resultado é descartado, sem sobrescrever as edições. Falhas são apresentadas na interface; rascunhos continuam persistidos.

Comparar exige confirmação de unidades independentes e de pressupostos conferidos; dados pareados ou desconhecidos direcionam ao resumo, sem executar indevidamente Student/ANOVA. As respostas são registradas com as observações. Não há verificação automática de normalidade/homogeneidade, nem teste pareado novo. O gráfico observado exibe pontos afastados horizontalmente para revelar coincidências, média e desvio padrão amostral identificados na legenda; o afastamento horizontal é somente visual, os valores medidos não são alterados.

Verificação local: 315 testes aprovados e Ruff aprovado. Abertura fria, mesma entrada PREP-003, com janela/processamento de eventos Qt: versão anterior 0,3877 s e revisão 0,0277 s no Mac de desenvolvimento. Matplotlib ausente da primeira abertura, sem confundir essa medida com tempo de análise/gráfico solicitado. Capturas a 880 px inspecionadas sem rolagem horizontal. Verificação empacotada/nativa desta versão em andamento; evidência final em interface/AUDIT.md.


A conferência do bundle encontrou o runtime hook pyi_rth_mplconfig do PyInstaller criando um diretório de fontes temporário a cada execução. A publicação 0.2.5 foi cancelada antes da release. Correção 0.2.6: cache de fontes persistente por caminho de instalação nos bundles onedir; se a pasta não puder ser criada, mantém o cache temporário. Primeiro carregamento da figura/fontes também roda em tarefa de fundo, tanto para simulação quanto para análise, mantendo o Qt na thread principal. Suíte ampliada para 317 testes, incluindo responsividade durante carga de fontes e estabilidade do cache.


Revisão final 0.2.7: seções recolhidas sem molduras que pareciam campos vazios; uma única exportação JSON no fluxo PREP. Pontos observados ocupam uma faixa ao lado da média, sem esconder a observação coincidente com ela. Capturas finais em `docs/interface/capturas/*-027.png`; quadro mínimo 880 px sem rolagem horizontal e resumo nativo conferido. A primeira carga de fontes pode levar segundos, com janela responsiva; cache de fontes permanece para as aberturas seguintes.


Entrega 0.2.7 conferida: 317 testes Mac; 316 Windows e um inaplicável. Executáveis e instalação Windows aprovados no CI 42551354018; instalado Mac local verificado e reaberto com registros pessoais preservados. Auditoria final em `docs/interface/AUDIT.md`. Não equivale a teste manual Windows, estudo de usabilidade ou validação em bancada.


## Importação Excel em desenvolvimento — 09/11/2026

Lucas escolheu reconhecer formatos comuns com prévia e atender tanto preparos/diluições quanto ensaios, sem prioridade exclusiva. Implementada primeira etapa no código: .xlsx, escolha de aba, reconhecimento de grupos em colunas, em linhas ou formato longo Grupo/Valor e prévia antes de substituir medições. Não executar fórmulas; exigir valores exportados para impedir uso silencioso de caches desatualizados. Limites de 20 MB/100.000 células. Grupos vazios, valores inválidos e não finitos são recusados; células vazias em séries são ignoradas e isso é informado. Dependência openpyxl (UI), carregada sob demanda.

Nove testes novos de reconhecimento/leitura e os 59 testes existentes de interface passaram. Ainda em desenvolvimento: leitura em segundo plano, rastreabilidade da importação, modelo Excel derivado do planejamento, desenho de ensaio com controles/tratamentos/repetições, correspondência de amostras/poços e revisão estatística completa. Não considerar esta etapa a entrega integral pedida por Lucas. Não foi instalada ou publicada nova versão com importação.


Autorização ampla de conclusão em 09/11/2026: critérios em `CONCLUSAO_APLICATIVO.md`. Implementados em desenvolvimento: leitura Excel em tarefa de fundo, descarte se o contexto mudar, arquivo/hash/aba/formato no payload de observações, gerador de coleta com identificadores e repetições e microplacas opcionais de 96 poços, planilha com observações vazias e contexto do planejamento. Interface para gerar o modelo integrada a Medições e análise. Teste do ciclo geração/preenchimento/reimportação e distribuição entre placas passou. Ainda não é entrega integral; faltam conferência completa de vínculo, persistência de desenho de ensaio, exportações de relatório/dados e inspeção/compilação final.


Continuação 09/11/2026: modelos agora incluem manifesto de coleta, registro e hash do plano. Reimportação confere identificadores únicos, completude, grupo, repetição, posição e unidade; recusado arquivo de outro planejamento. Organização e proveniência persistem no payload de observações. Geometrias de microplaca disponíveis de 6 a 384 poços. Exportação de dados CSV, pasta Excel com medições/resumo/rastreabilidade e relatório Word integrada. 72 testes dirigidos passaram (coleta/importação/exportações/interface), Ruff e diff-check aprovados. Pendente: relatório com plano/fontes completos e revisão visual; controles e desenho científico melhor representados; auditoria estatística e implantação final. Versão instalada permanece 0.2.8.


Continuação da conclusão: exportação Word agora inclui parâmetros e resultados planejados, procedimento e referências com páginas/URL/data de consulta; snapshot independente do plano acompanha a exportação. Interface da coleta pergunta controle e tipo de repetição; leituras técnicas bloqueiam comparação independente mesmo se a caixa de inferência for marcada. Núcleo estatístico recusa números não finitos/não reais e alpha fora do domínio aberto (0,1). Suíte completa de 330 casos passou após as alterações; acrescentados dez casos dirigidos de limites/relatório. Pendentes inspeção visual do relatório, auditoria integrada de importação e organização, ajuda/restauração, compilação e instalação final.
