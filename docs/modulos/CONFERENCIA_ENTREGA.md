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

## Distribuição pelo GitHub — 2026-11-08T19:28:57-03:00

A execução [42529979732](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions/runs/42529979732), commit `7bde4ae`, passou nos runners Windows 2025 x64 e macOS 15 Apple Silicon. Os 297 testes e o lint passaram em ambas as plataformas. O executável empacotado de cada plataforma verificou catálogo UTF-8, cálculo percentual, medições/estatística, histórico e exportação de dez POPs.

O instalador Windows passou por instalação silenciosa por usuário, abertura do aplicativo instalado, desinstalação e preservação de um registro acrescentado após instalar. O README oferece instalador Windows, ZIP portátil opcional e ZIP Mac. A publicação ocorre somente em tag de versão, após os dois builds passarem.

A falha `cp1252` da captura foi reproduzida na leitura sem codificação do catálogo e corrigida com UTF-8 explícito nos dois leitores. Formulários aceitam quebra de linha; Windows usa Segoe UI. As medidas de interface no runner Windows usam seu plugin Qt nativo, pois o plugin genérico offscreen apresentou métricas incompatíveis.

Limites: testes automatizados não equivalem a cliques manuais no PC de Lucas, avaliação com pesquisadores/leitor de tela ou validação em bancada. Instalador Windows sem certificado comercial de assinatura; pacote Mac com assinatura ad hoc, sem notarização Apple. As evidências acima atualizam a situação de empacotamento da tabela histórica sem apagar seus registros.
