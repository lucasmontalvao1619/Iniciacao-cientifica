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

Correção da conferência: ao abrir os relatórios JSON do CI 42529979732, foi encontrado erro de limpeza da base temporária SQLite após as verificações funcionais. O indicador `ok` havia sido marcado antes dessa limpeza. A publicação v0.2.0 foi cancelada, as conexões passam a ser encerradas e qualquer exceção agora define `ok=false`. A versão v0.2.1 exige uma nova execução sem esse erro; o CI anterior comprova as etapas funcionais, mas não uma verificação integral sem falhas.

## Conferência final da entrega v0.2.1 — 2026-11-08T19:42:44-03:00

A [versão publicada](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/releases/tag/v0.2.1), commit `0334edf`, foi aprovada integralmente no [CI 42530512091](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions/runs/42530512091). Os três relatórios `mac-smoke.json`, `windows-smoke.json` e `installed-smoke.json` foram baixados e conferidos: `ok=true`, sem campo de erro. Esta evidência substitui a pendência de limpeza do teste anterior.

| Requisito do pedido | Evidência conferida |
|---|---|
| Dez P1 originais com parâmetros próprios | PREP-001 a PREP-010 no catálogo; dez tipos de cálculo; testes independentes de fórmulas, unidades, limites e perguntas condicionais em `tests/test_preparos.py` e `tests/test_frontend.py` |
| Fontes da metodologia, dia/hora e origem | Todas as fontes técnicas correntes têm URL Arca/Anvisa/BVS MS, datas com fuso, páginas e SHA-256 correspondente aos cinco PDFs preservados; fichas e busca dirigida de edições em `docs/referencias` |
| POP individual, DOCX e imagens com fonte | Dez DOCXs extraídos do ZIP publicado e renderizados; todas as 23 páginas inspecionadas. Imagens, autoria, licença, URLs e datas presentes; hashes das três imagens conferidos. OOXML dos POPs Mac/Windows idêntico |
| Resultados e gráficos recalculados pela edição | Testes do fluxo específico de cada PREP, coordenadas/tabelas/gráficos e invalidação; integração de medições observadas aos dez protocolos, persistência e exportação |
| Histórico de dez e arquivo para consulta/exportação | Testes de limite, reinício, arquivamento automático/manual, somente leitura e preservação após erro de escrita; pasta `Registros de Experimentos` nos ZIPs |
| Mac e Windows nativo | Builds PyInstaller em cada SO, verificação do pacote e instalador por usuário. Mac publicado aberto nativamente em sessão isolada; tela inicial inspecionada e navegação até Protocolo observada pela árvore de acessibilidade |
| Pacote completo sem dados pessoais | CRC dos dois ZIPs aprovado; dez POPs ilustrados e pasta de registros; nenhum banco pessoal; catálogo empacotado com conteúdo JSON igual ao checkout (quebras de linha do Windows distintas). Downloads Windows/Mac retornaram HTTP 200 |
| Retirar linguagem de prévia do fluxo | Busca em Python/JSON do frontend sem ocorrências de prévia, demonstrativo ou não implementado; originais e registros anteriores preservados |

297 testes passaram em cada plataforma e o lint foi aprovado. Não houve mudança de cálculo nesta conferência. O processo Mac de QA usou dados temporários separados e foi encerrado; a sessão Desktop de Lucas foi preservada. O controle de cliques pelo Orca apresentou falhas de observação de janela após ações; não se declara percurso manual completo. A comprovação funcional dos dez fluxos vem dos testes de interface executados em ambos os sistemas, complementados pela verificação dos executáveis.

Entrega de software do escopo solicitado concluída. Isso não declara revisão sistemática integral, validação em bancada, teste com pesquisadores/leitor de tela ou assinatura comercial dos executáveis. Os limites técnicos específicos continuam no aplicativo e em cada POP.

## Atualização efetiva do aplicativo Desktop — 2026-11-08T19:49:22-03:00

A captura enviada por Lucas mostrava a cópia Desktop 0.1.0, ainda com cálculo somente de PREP-001. O catálogo dentro desse bundle foi lido: PREP-002 a PREP-010 não tinham `tipo_calculo`. O checkout e a release 0.2.1 já tinham os dez; a falha era a instalação local desatualizada.

A versão antiga foi fechada normalmente e preservada, junto com cópia dos dados existentes, em `output/atualizacao-desktop/20261108-194533`. O pacote publicado 0.2.1 foi instalado em `~/Applications/Planejador de Experimentos`, com atalho `~/Desktop/Planejador de Experimentos.app`. A localização evita metadados FinderInfo reaplicados pelo provedor de arquivos do Desktop. A assinatura do destino passou na verificação estrita. Os registros existentes do Desktop foram preservados; o caminho mostrado pelo aplicativo continuou sendo `~/Desktop/Registros de Experimentos`.

O aplicativo foi reaberto pelo atalho; versão e dez tipos de cálculo/fontes conferidos dentro da instalação. A verificação do próprio executável instalado terminou com `ok=true`, dez protocolos, cálculo de 9 g, média observada 4 e dez POPs exportados, sem erro. A interação nativa abriu Início e a lista com os dez protocolos; não se afirma seleção/cálculo manual de PREP-004, pois o controlador de acessibilidade perdeu a referência ao menu. Os testes específicos dos dez fluxos aprovados no CI da release continuam sendo a evidência funcional completa. Nenhuma alteração de cálculo foi necessária nesta atualização local.
