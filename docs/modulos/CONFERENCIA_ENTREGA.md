# Conferência da entrega dos dez PREP

Conferência em 2026-11-08T11:21:55.089869-03:00. Checkout ativo no Desktop, branch main. Esta tabela separa evidência de código/testes da execução nativa; não declara o objetivo completo.

| Pedido | Evidência atual | Situação |
|---|---|---|
| Dez P1 com os nomes da aba Protocolo | Catálogo `frontend/protocolos.json`, PREP-001 a PREP-010, prioridade P1; conferência de dez registros | Confirmado |
| Fontes nos portais da metodologia | Arca, Anvisa e BVS MS; PDFs preservados, fichas por protocolo e regularização Arca | Procedência confirmada; versões localizadas conferidas em busca dirigida documentada, sem inclusão formal no corpus |
| Origem, dia e horário por fonte | Catálogo/fichas contêm URL, obtenção, consulta com fuso, páginas e SHA-256; acessos antigos preservados | Confirmado para as regras implementadas |
| Parâmetros próprios e perguntas das variáveis | `frontend/preparos.py`, formulários de formulação/meio comercial, service e testes independentes dos dez cálculos | Confirmado no escopo documentado de cada PREP; condições faltantes ficam pendentes |
| POP individual visível e DOCX ilustrado | `frontend/pop.py`, dez DOCXs em `output/POPs`; testes de seleção/exportação e inspeções de páginas registradas | Confirmado; POPs são fichas individuais, sem alegar validação em bancada |
| Fonte das imagens | Autor, licença, URL, data e SHA-256; hashes das três imagens reutilizadas conferidos | Confirmado |
| Resultados e gráficos editáveis | `PreparoResults`, testes de edição/invalidação dos dez PREP e capturas Qt | Confirmado em Qt de desenvolvimento |
| Estatística ligada ao planejamento | Área observada dentro de Resultados, testes dos dez protocolos, JSON com contexto e gráfico de pontos | Confirmado; dados observados distintos dos planejados |
| Histórico de até dez e arquivo dos retirados | `Historico`, testes de limite/reinício/atualização/erro de arquivo; consulta somente leitura | Confirmado |
| Preservar medições e resultados arquivados | Rascunhos/análises no mesmo registro, fechamento/reinício e arquivamento imediato testados | Confirmado; falha de gravação agora tem recuperação explícita |
| ZIP com app, POPs e Registros de Experimentos | Pacote Mac r2, dez DOCXs e pasta de registros; assinatura, catálogo e CRC verificados | Mac empacotado; cliques no novo bundle ainda não repetidos |
| Aplicativo nativo Windows | Spec e PowerShell preparados, inclusive geração de POPs | PC disponível agora; pacote fonte preparado para compilação/teste no Windows |
| Retirar linguagem de prévia do fluxo real | Catálogo real só PREP, todos com cálculo; busca nas strings da interface | Fluxo principal sem essa linguagem; registros históricos e proteção de protocolos desconhecidos preservados |
| Tratar Markdown sem apagar informação única | Contexto atual com apontadores; originais e extrações preservados | Nenhuma remoção de conteúdo único nesta entrega |

Validação atual: 295 testes completos aprovados; três testes de recuperação repetidos após o ajuste visual final. Ruff e diff sem erros. Avisos: depreciação Starlette/httpx e caso SciPy degenerado esperado, recusado pela interface. Isso não substitui bancada, usuários/leitor de tela ou execução nativa Windows.

Conferência bibliográfica dirigida para as fontes do aplicativo concluída e registrada em `docs/referencias/REGULARIZACAO_FONTES.md`; nenhuma edição posterior do mesmo título/volume foi localizada nesse escopo. Isso não equivale à execução integral da revisão sistemática. Pendências para fechar o objetivo: verificação do pacote Mac em execução nativa e compilação/teste Windows no PC agora disponível. Não marcar a meta como concluída com essas evidências ausentes.
