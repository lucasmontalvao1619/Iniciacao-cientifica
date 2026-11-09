# Auditoria Visant Killer — prévia desktop

## Superfícies
| Tela | Tier | Superfície | Variável/tarefa |
|---|---|---|---|
| Início | T2 | B | Iniciar planejamento sem configuração extra |
| Protocolos | T2 | B | Selecionar exemplo e entender sua limitação documental |
| Parâmetros | T2 | B | Informar valores e unidades coerentes |
| Plano | T2 | B | Conferir entradas e saída do service antes de exportar |

## Verificações previstas
Abrir quatro telas, redimensionar, conferir navegação com preservação de dados, erro de domínio, exportação e foco por teclado. Registrar evidência abaixo após executar.

## Screen seen
| Tela | Tamanho | Dados | Evidência e resultado |
|---|---|---|---|
| Início | 1180×800 e 880×640 | Banco temporário, sem experimentos do usuário | `capturas/inicio-*.png`; título quebra linha no menor tamanho sem corte |
| Protocolos | Ambos | Dois registros do seed | `capturas/protocolos-*.png`; descrição e limitação documental legíveis; também inspecionada na janela real via acessibilidade |
| Parâmetros | Ambos | 8 amostras, 3 replicatas, 2 controles | `capturas/parametros-*.png`; formulário também aberto via acessibilidade na janela real; campos opcionais recolhidos para reduzir rolagem |
| Plano | Ambos | Resultado real do service com dados de exemplo | `capturas/plano-*.png`; tabela e procedimento com rolagem; aviso de material fracionado visível |

As oito capturas foram geradas por widgets Qt abertos em plataforma offscreen e inspecionadas visualmente. Janela nativa iniciada e identificada como “Planejador · Prévia da iniciação científica”. A interação na janela foi interrompida ao detectar ações do usuário; não se afirma percurso manual completo na janela nativa.

## Achados confirmados
- `frontend/app.py:219,245`: rótulo longo muito próximo do campo em janela estreita. Corrigido espaçamento horizontal de formulários para 24 px; captura revisada.
- `frontend/app.py:259`: campos de diluição sem uso ocupavam espaço e empurravam a ação principal. Corrigido com seção opcional recolhida por padrão.
- `frontend/app.py:342`: seed/service apresenta quantidades fracionárias para materiais indivisíveis, embora o dimensionamento de placas tenha outra regra. Exposto aviso na UI e exportação marcada demonstrativa; cálculo do backend não foi alterado nesta entrega. Permanece pendência científica/funcional antes de uso real.
- Ambiente macOS: plugins Qt marcados `hidden` pelo provedor de arquivos não eram encontrados. Inicialização limpa esse flag somente nos plugins desta instalação; depois disso teste e janela funcionaram.

## Interrogação da tela (T2)
1. A tarefa é clara? Sim: configurar e revisar um planejamento (app.py:143–355).
2. Precisa de login? Não; não foi acrescentado.
3. Há ação principal? Uma por tela, com retorno explícito.
4. Pode cortar conteúdo? Conteúdo longo usa QLabel com quebra e QScrollArea (app.py:49,115).
5. Há duplicação de entrada? Cada variável é coletada uma vez no formulário.
6. As unidades são explícitas? Diluição fixa mg/mL e mL; não há conversão automática.
7. O vazio informa o próximo passo? Início oferece novo planejamento sem experimentos fictícios.
8. A falha se distingue de zero? Erro de domínio mantém a configuração e exibe mensagem; testado.
9. O retorno preserva dados? Mesmo widget e teste de preservação.
10. O que falta para confiar no plano? Referência/edição/página e correção das regras de materiais; exposto.
11. Os resultados são independentes da aparência? Services existentes; teste confere 26 reações e alíquota de 1 mL.
12. O que ficou fora? Medições, estatística, gráficos, reimportação, persistência de rascunhos e catálogo científico completo. Não há controles fingindo esses recursos.

## Reuso, consistência e verificação
Widgets, ícone, foco e tema Qt; nenhum novo design system ou SVG. Mesma shell e função de página nas quatro etapas. Menor largura desktop 880 px; rolagem vertical deliberada para conteúdo longo. Não se afirma suporte móvel. Botão inicial acionado por Espaço em teste Qt; percurso completo de Tab e leitor de tela não auditados. Sem animações ou rede neste fluxo; testes de backend HTTP indisponível e métricas de conversão não se aplicam. Performance não foi medida.

Teste direcionado: 37 testes em `test_frontend`, `test_calculos` e `test_services`; ruff e formatação dos novos arquivos. Backend não foi modificado. A suíte completa da API/estatística não foi repetida, pois essas camadas não sofreram mudanças.

Conclusão: prévia navegável para discutir fluxo e layout, com limitações documentadas. Não é liberação científica nem aprovação completa pelos gates upstream.

## Gates e limites
Scripts upstream killer/refine/copy/noise/verify-screens não fornecidos; não executados. Skills auxiliares visant-frontend/motion/copy/refine e revenue-centric-design ausentes; julgamento manual baseado na skill local. HSL CSS e regras Tailwind não se aplicam ao PyQt6; QPalette e widgets/ícones Qt substituem tokens e primitives web. Sem animações decorativas. Sem nota quantitativa, pois não há rubrica e detectores originais completos.

## Atualização: navegação pelas quatro etapas

Defeito confirmado: `PlannerWindow.__init__` criava QLabel para as etapas laterais, impossibilitando o clique solicitado. Substituído por QPushButton checkable, com um único destaque e foco nativo. `navigate` recalcula Plano e bloqueia avanço em erro. Dados preservados nas outras três áreas.

As quatro telas foram renderizadas após acionamento dos botões em Qt offscreen (`capturas/navegacao-1.png` até `navegacao-4.png`); a captura de seleção foi inspecionada visualmente, com realce apenas na etapa atual. Testes direcionados: 38 aprovados, incluindo navegação lateral, edição após geração, troca de protocolo e bloqueio com título vazio. A janela antiga precisa ser reaberta para carregar esta atualização; não foi encerrada automaticamente para preservar a interação do usuário.

## Atualização: dez P1 e pesquisa local

Seleção autorizada por Lucas: PREP-001 a PREP-010, identificadores P1 do catálogo F03. Lista agora contém dez candidatos e dois exemplos. Registro de origem e data/hora de consulta ao catálogo em JSON e dez fichas Markdown. As fontes primárias e cálculos específicos não foram inventados nem considerados prontos.

Navegação lateral passa a abrir sempre a página solicitada, inclusive Plano em caso de erro ou regra pendente. Nesses casos apresenta mensagem e desabilita exportação; a ação de gerar no formulário continua mostrando seus erros no formulário. Pesquisa ignora acentos e caixa, busca nome/código, permite limpar e tem estado sem resultados.

Inspeção Qt offscreen em 1180×800 e 880×640: `capturas/catalogo-*.png`. Defeito confirmado na seleção a 880 px: tamanho mínimo de QComboBox e textos longos forçavam rolagem horizontal. Ajustados size policies Qt e tamanho mínimo do combo; nova captura mostra zero de rolagem horizontal. Teste percorre cada um dos dez códigos em janela estreita, além de pesquisa por nome sem acentos, código, nenhum resultado e retorno à lista completa. Sem gates web upstream, conforme limites já registrados.

## Atualização: dropdown e sequência com reset

Pesquisa movida para QComboBox editável com completer nativo, filtrando por nome/código sem acentos. O campo separado foi removido. Protocolo precisa ser escolhido e confirmado antes de liberar Parâmetros; Plano só é liberado após cálculo válido. Trocar protocolo ou iniciar novo planejamento limpa título, restaura campos aos valores iniciais e apaga saídas; alterar parâmetro invalida plano e exportação. Guardas também existem nas funções, além dos botões desabilitados. O catálogo de candidatos continua sem regras inventadas.

39 testes direcionados aprovados após adequação às novas regras. Capturas Qt `dropdown-pesquisa.png` e `dropdown-resultados.png` inspecionadas: pesquisa no próprio seletor e três correspondências para “diluicao”. Sem gates web upstream. Testes cobrem confirmação, texto livre inválido, resets, bloqueios, erro científico e exportação.

## Consolidação e área de análise

Mantida uma única aplicação da pasta Desktop/INICIACAO CIENTIFICA; QLockFile impede segunda instância. Validação operacional: segunda invocação terminou com “O Planejador já está aberto” e listagem mostrou apenas um processo frontend.app.

Análise é T2/B, tarefa de conferir medições, resumos e pontos antes de interpretar. Entrada explícita em memória, exemplo carregado apenas por ação do usuário, inferência opcional. Services existentes preservados. Renderizações `analise-grafico*.png` inspecionadas em 1180 e 880 px. Defeitos confirmados: cabeçalhos cortados e gráfico comprimido se sobrepondo à ação em janela pequena. Correções: ajuste de cabeçalhos, altura mínima do canvas e conteúdo em área rolável; sem overflow horizontal no menor tamanho. O scroll vertical é deliberado. PNG de figura salvo em teste e assinatura verificada. Não houve testes com leitor de tela nem gates upstream ausentes.

49 testes direcionados: frontend, cálculos, services e estatística. Incluem busca integrada sem acentos, confirmação e bloqueios, reinício/troca de protocolo, invalidação de plano, média independente por grupo, inferência opcional, dados não finitos e geração de PNG. Persistência de medições, todos os gráficos futuros e validação científica dos dez candidatos continuam fora desta entrega.

## Acessibilidade prática e processo integrado

Defeito de navegação confirmado: análise estava em aba independente e não recebia identificação do planejamento. Substituída por etapa Resultados na mesma shell, liberada após plano válido, com botão de continuidade e retorno. O contexto agora acompanha resumos, unidade e gráfico; JSON agrega os dados observados e a análise ao plano. Invalidar plano limpa medições e resultados, com teste de associação de protocolo e ausência de dados sintéticos.

Defeito de interação confirmado: o clique no texto do seletor não abria sugestões. SearchableProtocolBox usa eventFilter de clique e completer Qt nativo; teste Qt cobre clique, popup aberto, digitação, redução a uma correspondência e seleção por mouse. Não houve alteração de fonte científica.

A entrada estatística deixa de exigir CSV: tabela com nome do grupo e lista de valores, inclusão/remoção de grupos e unidade identificada. Mensagens posicionam o foco no dado faltante e recusam grupo duplicado/valor não finito. Opções técnicas de comparação recolhidas inicialmente. Resultado explica média/desvio e preserva a distinção entre parâmetros e observações. Controles usam Qt nativo, labels, cabeçalhos, buddy da unidade, foco e indicação de desabilitado.

Capturas `fluxo-resultados-1180.png`, `fluxo-resultados-880.png`, `resultados-completo.png` inspecionadas: sem overflow horizontal em 880 px, título quebra corretamente, gráfico legível e rolagem vertical deliberada. 50 testes direcionados (frontend/cálculos/services/estatística) aprovados. Não foram usados detectores web ausentes nem atribuída nota automática; leitor de tela, zoom do sistema e ensaio de usabilidade com participantes não foram avaliados.

Verificação nativa final: janela “Planejador de Experimentos” aberta após a atualização; árvore de acessibilidade confirma cinco etapas, com Parâmetros/Plano/Resultados inicialmente desabilitados e descrições dos pré-requisitos. Mantida uma instância.

## Bundle macOS e identidade do aplicativo

Ícone original gerado por imagegen e salvo em `frontend/assets/app.png`; ICNS derivado por redimensionamento e iconutil. QApplication e Info.plist identificam Planejador de Experimentos, bundle ID `br.lucasmontalvao.planejador`.

Construção PyInstaller 6.22.3 para macOS arm64, saída em `/private/tmp/planejador-build/Planejador de Experimentos.app`. Assinatura ad hoc verificada com codesign --verify --deep --strict no artefato de construção. Cópia no Desktop conferida por SHA-256 dos 625 arquivos regulares. Metadados do Finder podem reaparecer em cópias no Desktop; não foram removidas proteções do sistema nem aplicada notarização Apple. O teste de abertura foi realizado na cópia do Desktop.

A janela nativa identifica App e menu como Planejador de Experimentos, não Python. Catálogo com dez candidatos e dois exemplos carregado do bundle. A ativação de um botão lateral pela acessibilidade inicialmente apenas alterava seu estado; conexão de toggled corrige o encaminhamento. Novo teste verifica a ativação por estado; nova compilação validada na janela nativa passando de Início a Protocolo com destaque único.

88 testes da suíte completa passaram; ruff check backend/frontend/tests, formatação e diff --check passaram. Um aviso de depreciação da dependência Starlette/httpx foi emitido, sem falha. `.venv`, build e bundles não entram no Git; fontes, ícone e receita de compilação são versionados.

## Abertura: carregamento sob demanda

A janela inicial construía AnalysisWidget e importava SciPy/Pandas/Matplotlib antes de aparecer. Além do import da UI, `services.__init__` carregava estatística e o módulo de experimentos importava tabelas globalmente. Foram adiados a resolução dos serviços estatísticos, o import das tabelas de experimento e a construção/import da UI de Resultados.

Medição local no modo de desenvolvimento, com Qt offscreen, neste Mac: antes, 1,762 s de imports e 2,010 s até renderização inicial; depois, 0,386 s de imports e 0,577 s até renderização. Amostras pontuais, não benchmark de inicialização fria do executável nem medição em Windows. Nenhuma promessa de tempo máximo de abertura.

Teste em processo Python isolado confirma ausência de SciPy, Pandas, Matplotlib e frontend.analysis ao abrir a janela, e ausência de SciPy durante o planejamento; ao entrar em Resultados, os módulos e a tela são carregados com o experimento correto. Estatística e exportações foram preservadas. A suíte completa passou com 89 testes.

Executável macOS reconstruído e cópia do Desktop atualizada. Verificação na janela nativa: abertura inicial, seleção de protocolo, geração do plano e primeira entrada em Resultados com o experimento correto. A primeira entrada em Resultados ainda teve espera perceptível durante o carregamento das bibliotecas; não foi atribuído tempo instrumentado a essa etapa. Dados de teste removidos pelo fluxo Novo planejamento e aplicativo deixado na tela inicial. A medição de 0,577 s acima se refere ao código de desenvolvimento, não ao bundle ou ao Windows.

## Correção do bloqueio entre Parâmetros e Plano

Causa confirmada: `generate` retornava antecipadamente para qualquer identificador textual (os dez candidatos P1), mantendo o usuário na etapa Parâmetros. A revisão permite gerar uma prévia explicitamente pendente com os parâmetros, sem inventar insumos ou cálculo científico. `pendente` acompanha o plano exportado e bloqueia Resultados, inclusive pelo guard de navegação. Os exemplos numéricos mantêm seus cálculos reais. Nome inicialmente preenchido a partir da seleção elimina o requisito pouco perceptível de preencher um título para avançar.

Testes percorrem os dez candidatos e conferem avanço, marcação pendente, ausência de insumos e bloqueio de análise operacional. Captura Qt `plano-preliminar.png` gerada para PREP-004.

Validação final: 90 testes passaram, Ruff e diff --check sem erros. Bundle macOS reconstruído e verificado em /private/tmp; cópia do Desktop atualizada. Na janela nativa, PREP-004 foi selecionado, confirmado e avançou de Parâmetros para Plano pelo botão Gerar prévia do plano; título automático presente e Resultados desabilitado por pendência científica. Windows não verificado nesta correção.

## Prévia do POP separada do avanço

A pedido de Lucas, Parâmetros passa a ter um botão secundário de largura natural,
Gerar prévia do POP, e a ação principal Seguir para Plano. A prévia usa diálogo
Qt de leitura com fechamento por botão/teclado, permanece na etapa atual e não
invalida o plano/análise existentes. O cálculo compartilhado valida antes de
abrir a prévia ou avançar. Não foram acrescentados procedimentos científicos nem
fontes; conteúdo pendente continua indicado explicitamente.

Verificação desta alteração: 93 testes passaram, Ruff e diff --check sem erros.
Testes cobrem prévia de exemplo/candidato, validação de entradas, permanência em
Parâmetros, preservação de plano existente e avanço pelo botão principal.
Capturas Qt inspecionadas: `parametros-acoes.png` e `previa-pop.png`. Bundle macOS
reconstruído, assinado/verificado em /private/tmp e copiado para o Desktop.
A janela instalada mostrou os dois botões e o protocolo selecionado; a tentativa
de conferir os cliques por automação nativa sofreu timeout enquanto a janela
mudava, portanto não é registrada como verificação completa dos cliques no
bundle. Windows não foi testado nesta alteração.

## Catálogo restrito a PREP

A pedido de Lucas, removidos da lista pesquisável os dois exemplos sem prefixo.
A seleção e suas sugestões contêm somente PREP-001 a PREP-010; descrição da tela
atualizada. Os exemplos de cálculo permanecem apenas no backend e nas fixtures
de testes. Como os dez PREP ainda estão pendentes, Resultados não é liberado
por nenhum item atualmente disponível na interface.

Catálogo PREP: 93 testes passaram; lint e diff --check sem erros. Bundle macOS
reconstruído e cópia do Desktop atualizada. A sessão aberta não foi encerrada;
reabrir o aplicativo aplica a nova lista. Windows não testado nesta alteração.

## POP na seleção do protocolo e exportação Word

Gerar prévia do POP foi movido de Parâmetros para 2 · Protocolo. Consulta e DOCX
usam as mesmas seções e os metadados próprios do PREP selecionado; ficam
indisponíveis para texto sem correspondência no catálogo. A prévia não confirma
o protocolo nem altera parâmetros/plano. DOCX disponível na página e no diálogo,
com tratamento de cancelamento/erro. `python-docx` entrou no extra ui e é
importado somente na exportação. Não houve obtenção de novas informações
científicas; origem/datas preservam o catálogo e não simulam leitura primária.

Verificação: 10 testes de interface passaram, incluindo os dez PREP distintos,
preservação do plano, exportação, cancelamento e falha ao salvar; Ruff e
diff --check passaram. Capturas Qt da seleção e do diálogo inspecionadas. DOCX
de PREP-001 (maior registro em caracteres) renderizado pelo LibreOffice do
runtime e sua página conferida, sem cortes. Windows não testado nesta alteração.

Bundle macOS reconstruído e verificado em /private/tmp, cópia do Desktop
atualizada com template DOCX incluído. Reabrir o aplicativo carrega a alteração;
a sessão em uso não foi encerrada. Cliques no bundle não foram retestados nesta
entrega; comportamento verificado pelos testes e capturas Qt de desenvolvimento.

## Entrega incremental PREP-001 em 08/11/2026

O estado demonstrativo foi substituído por cálculo percentual rastreável. Os parâmetros são específicos e Resultados oferece edição com gráfico de dimensionamento, sem simular observações. Histórico SQLite de dez com arquivo de excedentes/retirados foi adicionado e testado, inclusive falha de gravação. Demais PREP permanecem sem liberação operacional.

117 testes da suíte completa passaram; 22 testes de cálculo/histórico repetidos após ajuste numérico. Ruff e diff --check sem erros. Verificação tipada dos três módulos novos com imports omitidos passou; com dependências houve erro em stubs PyQt6/QtGui, sem aprovação de tipagem completa. Capturas finais PREP-001-parametros/resultados/historico.png inspecionadas. POP de PREP-001, com imagem complementar e fontes identificadas, renderizado e conferido em duas páginas.

Bundle Mac reconstruído e assinatura verificada em /private/tmp; cópia Desktop e ZIP com pasta de registros e POP atualizados. A sessão aberta não foi encerrada; reabrir para carregar a nova versão. Windows apenas preparado em script/spec, a pedido de Lucas, que não dispunha do PC para teste. Plano integral e pendências: ../modulos/IMPLEMENTACAO_PREP.md.

## PREP-002 em 08/11/2026

Preparo molar a partir de reagente pesado ou líquido medido por volume. Massa molar e teor m/m correspondem à forma química identificada; densidade do reagente comercial é solicitada somente no modo volumétrico. Core e service utilizam Fiocruz 2009, p. 226, 229–232 e 249–250, com consulta e imagem complementar registradas. Os parâmetros/resultados percentuais e molares compartilham frontend/preparos.py e permanecem distintos na exportação.

139 testes da suíte completa passaram, incluindo casos independentes, exemplo arredondado de HCl da fonte, entradas inválidas, troca de tipo de protocolo, resultado/gráfico ao vivo, histórico e DOCX ilustrado. Testes de comparação de números fracionários usam tolerância explícita onde necessário para representação binária; não se trata de tolerância de equipamento. Ruff e diff --check sem erros; core/service alterados passaram em mypy com imports omitidos (não é verificação tipada completa das dependências).

Capturas PREP-002-parametros/resultados.png e as duas páginas do DOCX inspecionadas. Bundle Mac reconstruído, assinatura verificada em diretório temporário. ZIP PREP-001-002 inclui ambos os POPs, recursos e Registros de Experimentos, com conteúdo e CRC conferidos. A cópia aberta do Desktop não foi substituída: instalar o ZIP após fechar a versão em uso. Windows permanece preparado para execução posterior, conforme escolha de Lucas. Demais oito PREP não foram liberados.

## Perguntas variáveis e PREP-003 em 08/11/2026

Perguntas condicionais e valores físicos inicialmente não respondidos nos três preparos. Identidade livre opcional e informações de rótulo pendentes sem impedir o cálculo. PREP-003 exige equivalência específica quando as unidades certificadas precisam de conversão entre atividade e massa. Testes de formulário, cálculo, recálculo/gráfico, histórico, JSON e DOCX passaram: 163 testes na suíte completa; Ruff aprovado. Aviso existente Starlette/httpx. Ainda sem nova inspeção visual ou novo pacote nesta alteração; Windows não executado.


Conferência final PREP-003: 165 testes passaram, Ruff e diff --check sem erros. A inspeção revelou perguntas muito estreitas, largura mínima excessiva nos campos de atividade e corte do texto explicativo ao redimensionar. Corrigidos em frontend/preparos.py e cobertos por teste de janela mínima com diferentes unidades e identificação expandida. Capturas PREP-003-parametros/resultados.png conferidas; gráfico de dimensionamento, dose corrigida por potência e fonte exportável preservados. POP individual renderizado e inspecionado nas três páginas, com crédito da imagem. Build Mac final com assinatura local verificada e ZIP íntegro com três POPs e pasta de registros. Catálogo empacotado idêntico ao código. Sessão Desktop em uso não substituída; Windows ainda não executado.

## PREP-004 em 08/11/2026

Perguntas de diluição específicas; sem perguntas de pureza, massa molar ou frasco que não entram no cálculo. Alíquota e fator explícitos, C1/C2 na mesma base, q.s.p. sem afirmar aditividade de volumes. Fonte Fiocruz p. 230–232 registrada. Reutilização do cálculo existente com validação de finitude/tipo, conservação verificada independentemente, unidade incompatível rejeitada. 181 testes passaram na suíte completa; Ruff aprovado e mypy com imports omitidos nos módulos alterados, sem alegar tipagem completa. Capturas PREP-004-parametros/resultados.png e duas páginas do DOCX inspecionadas; janela mínima de 880 px sem rolagem horizontal, texto explicativo sem corte. Resultados recalcula gráfico e atualiza o mesmo registro do histórico, inválidos retiram plano/gráfico exportável. Windows e bancada não testados.

Pacote Mac PREP-001-a-004 gerado; assinatura local verificada, catálogo empacotado idêntico ao código, quatro DOCX e pasta de registros incluídos, CRC aprovado. Sessão aberta do Desktop preservada, sem novos cliques no pacote.

## PREP-005 em 08/11/2026

Perguntas específicas para série, excluindo estoque da contagem, distinguindo volume preparado de remanescente e retirada opcional do último. Tabela nativa Qt compartilhada entre Plano/Resultados; gráfico em escala logarítmica, com estoque na etapa 0 e eixo inteiro. Entradas numéricas não presumidas, identidade opcional; sem perguntas de teor ou massa molar. 202 testes passaram na suíte completa, Ruff e diff --check aprovados, mypy core/service com imports omitidos aprovado. Balanços de volume/soluto e desenho do gráfico em faixa extrema testados. Capturas PREP-005-parametros/plano/resultados.png e três páginas do DOCX inspecionadas; página de 880 px sem rolagem horizontal, texto explicativo sem corte. Windows e bancada não testados.


Pacote Mac PREP-001 a PREP-005: `output/distribuicao/Planejador-Mac-PREP-001-a-005.zip`, com aplicativo, cinco POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Ajuste final de margens do gráfico seguido por 19 testes de interface aprovados. Sessão Desktop preservada; fluxo conferido em Qt de desenvolvimento, sem novos cliques no pacote. Windows permanece preparado para execução posterior, conforme escolha de Lucas.

## PREP-006 em 08/11/2026

Cálculo inverso de diluição, com C1/V1/V2 perguntados e F/C2 como saídas. Campos físicos sem resposta inicial, identificação opcional, demais parâmetros de preparo ocultos e excluídos da exportação. Gráfico explicita C1/alíquota fixos, V2 variável e ponto do preparo. Fonte Fiocruz p. 230–232 consultada localmente, data/hora/hash registrados. 219 testes passaram, incluindo preservação dos volumes informados, valores extremos sem estouro intermediário, limites, mudanças de protocolo, gráfico, histórico e DOCX. Ruff e diff --check aprovados, mypy core/service com imports omitidos aprovado; sem tipagem completa. Capturas PREP-006-parametros/resultados.png e duas páginas do DOCX inspecionadas; página de 880 px sem rolagem horizontal e texto explicativo sem corte. Windows e bancada não executados.


Pacote Mac PREP-001 a PREP-006: `output/distribuicao/Planejador-Mac-PREP-001-a-006.zip`, com aplicativo, seis POPs e pasta Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows continua com compilação/teste preparado para execução posterior no PC, conforme escolha de Lucas.

## PREP-007 em 08/11/2026

Perguntas específicas para v, N e E, com unidade explícita e zero excedente permitido; nenhuma margem positiva presumida. N inclui controles/repetições já contados. Saídas separadas base/reserva/total e gráfico comparativo por número de unidades. Nomes opcionais; sem campos de concentração/pureza ou solvente. 237 testes passaram na suíte completa, incluindo limite de um milhão com gráfico limitado a 21 pontos, entradas inválidas e recálculo/histórico/JSON/DOCX. Ruff e diff --check aprovados, mypy core/service com imports omitidos aprovado. Capturas PREP-007-parametros/resultados.png e duas páginas do DOCX inspecionadas; página de 880 px sem rolagem horizontal. Nova fonte BVS e imagem original creditada registradas; sem aplicar regra +1/+2 reações a todo laboratório. Windows e bancada não executados.


Pacote Mac PREP-001 a PREP-007: `output/distribuicao/Planejador-Mac-PREP-001-a-007.zip`, com aplicativo, sete POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, três imagens de equipamentos e CRC conferidos. Após o ajuste final do texto explicativo, 153 testes de cálculo/interface passaram novamente. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows permanece preparado para compilação/teste posterior no PC, conforme escolha de Lucas.

## PREP-008 em 08/11/2026

Painel de formulação sob demanda, referência identificada/protegida e receita livre com autoria separada. Quantidades nominais não são convertidas em q.s.p.; fonte Anvisa p. 15 (PDF 17) conferida visualmente. pH e conservação dessa receita preservados; ciclo ausente perguntado, sem valores universais. Ciclo anterior limpo ao trocar a formulação. Tabela de entradas com linhas ajustadas ao tamanho real dos controles; cabeçalho antes cortado foi corrigido. Resultados exibe quantidades escaladas e gráfico por componente, sem somar unidades incompatíveis. 251 testes passaram, Ruff/diff --check aprovados, mypy core/service com imports omitidos aprovado. Capturas PREP-008-parametros/resultados.png e duas páginas finais do POP inspecionadas; imagem reduzida nesse documento para manter créditos completos na mesma página. Página de 880 px sem rolagem horizontal e rótulos sem corte. Windows e bancada não executados.


Pacote Mac PREP-001 a PREP-008: `output/distribuicao/Planejador-Mac-PREP-001-a-008.zip`, com aplicativo, oito POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Módulo frontend.formulacao confirmado no arquivo PYZ; teste do fluxo de formulação passou novamente após ajuste final da altura das linhas. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows permanece preparado para compilação/teste posterior no PC, conforme escolha de Lucas.

## PREP-009 em 08/11/2026

Painel comercial sob demanda, reutilizando núcleo de escala. Três números inicialmente sem resposta e convenção de volume escolhida explicitamente. Sem proporção/ciclo universais. Referência do fabricante declarada, não confundida com consulta da fonte Anvisa. Preparo, pH, suplementos, ciclo e conservação perguntados; faltantes pendentes. 265 testes passaram, Ruff/diff --check aprovados, mypy service com imports omitidos aprovado. Capturas PREP-009-parametros/resultados.png e duas páginas do DOCX inspecionadas; página de 880 px sem rolagem horizontal e rótulos sem corte. Caso numérico sintético está identificado como teste, sem prescrição atribuída a um fabricante. Windows e bancada não executados.


Pacote Mac PREP-001 a PREP-009: `output/distribuicao/Planejador-Mac-PREP-001-a-009.zip`, com aplicativo, nove POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Módulo frontend.meio_comercial confirmado no PYZ. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows permanece preparado para compilação/teste posterior no PC, conforme escolha de Lucas.


## PREP-010 implementado — 08/11/2026

Dimensionamento de meio para placas ou tubos, dose, unidade, contagem já incluindo controles/repetições e excedente escolhido. Formato/capacidade e método declarados separadamente, ausências pendentes. Um tipo de recipiente e uma dose por planejamento; sem dose universal, massa de pó ou condições automáticas. Fontes Anvisa p. 18 (PDF 20) e BVS MS p. 48 (PDF 49), horários/hashes e adaptação registrados. Gráfico por número de recipientes com edição ao vivo, mesmo histórico e exportação JSON com proveniência.

280 testes passaram, Ruff aprovado e mypy do service com imports omitidos aprovado (não equivale a tipagem completa das dependências). Capturas Qt a 880 px e gráfico inspecionados; sem rolagem horizontal da página. POP ilustrado renderizado em três páginas e integralmente inspecionado; corrigida no exportador comum a separação entre imagem e créditos. Não houve teste de leitor de tela ou validação em bancada.

Os dez PREP têm dimensionamento, perguntas e POP individuais. A integração final de medições observadas/estatística ao fluxo desses protocolos ainda falta; não confundir seus gráficos de dimensionamento com análise de observações. Windows continua preparado para compilação/teste posterior no PC, conforme decisão de Lucas.


## Integração de medições — 2026-11-08T11:07:39.590797-03:00

Integração de medições aos dez PREP inspecionada em Qt de desenvolvimento, a 880 px. Corrigidas margem duplicada que causava 16 px de rolagem horizontal, cabeçalho de entrada cortado e largura excessiva do resumo. A seção observada fica recolhida até o pesquisador abri-la. 292 testes completos passaram; 12 de integração repetidos após ampliar a cobertura de gravação e arquivo. Não atribuído score ou aprovação de gates upstream; leitor de tela e bundle/Windows não testados nesta atualização.


## Preservação de gravação — 2026-11-08T11:21:55.089869-03:00

Falha de gravação simulada: o fechamento antes permitido foi bloqueado, assim como arquivo e troca de protocolo, com exportação de recuperação explícita. Inspeção a 880 px confirmou ação visível sem rolagem horizontal. 295 testes completos e três de recuperação repetidos passaram; sem score/gates web ou alegação de teste nativo.

## Correção de gravação e clareza — 08/11/2026

| Região | Tier/superfície | Tarefa | Defeito confirmado | Verificação prevista |
|---|---|---|---|---|
| Início e Novo planejamento | T3/C | Preservar e iniciar experimentos | Conexão SQLite anterior à mudança de pasta falha com SQLITE_READONLY_DBMOVED e bloqueia reinício; reproduzido em teste real | Recuperação da conexão, persistência, botão real e falha genuína de permissão |
| Aviso do histórico | T2/B | Entender falha e recuperar dados | SQL/JSON técnico ocupa a tela inteira em save_history | Mensagem curta, ação de repetir e detalhes recolhidos |
| Ficha de protocolo | T2/B | Entender finalidade e consultar fontes | Descrição concatena estado interno, catálogo, data ISO e URL longa | Finalidade legível; fontes/datas/links preservados sob expansão; 880 px |

Gates disponíveis: pytest e Ruff. Scanners upstream Visant ausentes nesta instalação local; não executados. Sem pontuação inventada. Dados pendentes reais de PREP-004 exportados para arquivo de recuperação e reinseridos no histórico antes de encerrar a sessão antiga.

### Screen seen — conferência desta correção

| Tela | Largura/dados | Ação e resultado |
|---|---|---|
| Protocolo | 880 px, PREP-004 | Captura Qt aberta e inspecionada: título/finalidade separados; URLs e datas fora do resumo |
| Fontes e rastreabilidade | 880 px, PREP-004 | Expansão conferida em captura Qt: referência, páginas, data legível e link para obra/catálogo preservados |
| Início com falha | 880 px, falha simulada sem dados reais | Mensagem curta, exportação, tentativa de salvar e detalhes recolhidos; tabela vazia substituída por estado vazio |

Teste real reproduziu conexão SQLite após mover a pasta; correção reconecta uma vez somente para SQLITE_READONLY_DBMOVED. Erro SQLITE_READONLY genuíno não é repetido nem mascarado. O clique real em Novo planejamento preserva medições anteriores, limpa seleção/parâmetros e permite confirmar outro protocolo. Suíte de 302 casos aprovada antes do ajuste visual final; 44 testes de interface aprovados após o ajuste de espaçamento e altura do histórico, Ruff aprovado. A interface utiliza QPalette/widgets Qt; gates web não se aplicam. Compilação/pacote atualizado e verificação nativa ainda em andamento nesta anotação.

Conclusão v0.2.2: [CI 42534871665](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions/runs/42534871665) aprovado; Mac 302 casos, Windows 301 aprovados e um caso de movimentação de diretório SQLite aberto inaplicável nesse SO. Relatórios dos dois executáveis e do instalado Windows conferidos sem erro. Instalação Mac local 0.2.2 atualizada sem mover novamente os dados; verificação empacotada aprovada. Ficha nativa PREP-003 inspecionada em janela de 1180×828, com resumo limpo e fontes recolhidas; histórico recuperado foi visto no Início. A API de controle visual apresentou um timeout após clique, então a prova do fluxo completo de reinício continua sendo o teste Qt de regressão, não uma alegação de percurso manual integral. Os dados reais de PREP-004 foram preservados; a cópia de recuperação e o arquivo posterior continuam em Registros de Experimentos. Sem score/gates upstream ou teste manual Windows.

## Resultados, entrada numérica e consulta — 08/11/2026

| Região | Tier/superfície | Defeito confirmado | Correção e conferência prevista |
|---|---|---|---|
| Primeira abertura de Resultados | T2/B | Perfil em processo frio: importação estatística dentro de AnalysisWidget consumiu 2,0 s; abertura sem perfil levou 1,985 s | Importar motor estatístico somente ao analisar medições válidas; garantir gráfico de dimensionamento e análise posterior |
| Campos numéricos | T2/B | Digitação inicial sobre “Informe o valor” não substituía o texto; ponto decimal era interpretado como milhar no locale local | Editor numérico Qt seleciona a dica ao focar/clicar; aceita ponto/vírgula; limites preservados. Recalcular ao confirmar/terminar edição, sem gravar/desenhar a cada tecla |
| Botão Consultar | T1/B | Botão sem fundo próprio deixava aparecer a cor de seleção da célula | Fundo neutro explícito por QPalette, preservando foco, primários e navegação; conferir clique/fechamento e cor renderizada |

A seção opcional de estoque identifica frasco/lote/responsável e condições definidas pelo método; não inventa validade nem interfere nos números essenciais. Explicação fornecida a Lucas, sem retirar informações do protocolo.

### Conferência 0.2.3

Processos frios no Mac de desenvolvimento: abertura de Resultados PREP-003 de 1,985 s para 0,586 s, com as mesmas entradas; reaberturas anteriores já eram rápidas. Medida local, não benchmark universal de Windows. Teste em subprocesso garante que Resultados desenhe sem importar o motor estatístico e que a análise posterior continue retornando média correta. Digitação direta e ponto/vírgula foram conferidos com QTest e as setas permanecem disponíveis. Digitar não dispara valueChanged até confirmar ou sair do campo, evitando processamento a cada tecla. Cor renderizada do botão Consultar permanece igual à cor neutra após fechar com aceitar ou X, sem apagar foco por código. Suíte de 309 testes aprovada; Ruff aprovado.

A conferência visual encontrou texto indevidamente escuro nos botões desabilitados após definir cor global; a compilação 0.2.3 foi cancelada antes de publicar. A versão 0.2.4 define somente o fundo neutro e preserva a cor desabilitada do QPalette, com teste específico. Capturas Qt finais a 880 px foram abertas: entrada direta 12,5 confirmada como 12.5; Resultados com gráfico e consulta encerrada com botão branco. Suíte completa de 310 casos e teste adicional de confirmar número ao clicar em outra ação passaram; nenhum dado digitado foi perdido por exigir Enter. As setas, limites e unidades permanecem. Build/pacotes nativos desta atualização ainda em conferência.


Conclusão v0.2.4: [CI 42536815468](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions/runs/42536815468) aprovado: Mac 311 testes; Windows 310 aprovados e um caso de movimentação SQLite aberto inaplicável no sistema. Executáveis Mac/Windows e instalado Windows passaram na verificação empacotada: dez protocolos, dez DOCX e análise observada conferidos. Instalação Mac local atualizada, verificação empacotada aprovada e instaladores locais substituídos pelos assets v0.2.4, ZIP conferido sem erro.

Conferência nativa do instalado Mac em sessão temporária separada dos dados pessoais: primeiro clique em Informe o valor permitiu digitar 1,5, confirmado como 1.5; 100 mL e pureza 100% produziram 150 mg em Plano e Resultados. A primeira abertura também gerou o cache de fontes Matplotlib nessa sessão temporária; esse trabalho inicial pode causar espera adicional à medição de desenvolvimento. A consulta foi aberta pelo teclado e encerrada por Fechar consulta; captura confirmou botão branco, com indicação de foco preservada. Dados pessoais e arquivos históricos não foram alterados nessa sessão. A sessão temporária foi encerrada e o aplicativo normal reaberto; a API visual apresentou timeout ao tentar inspecionar a nova janela. Sem teste manual no Windows, score ou gates upstream.


## Reorganização de Resultados — 08/11/2026

| Região | Tier/superfície | Defeito confirmado / tarefa | Verificação prevista |
|---|---|---|---|
| Resumo e ajustes | T2/B | PreparoResults repete formulário acima do resumo | Resumo primeiro, parâmetros recolhidos, cálculos de dez PREP preservados |
| Gráficos | T2/B | Canvas e figuras criados antes de solicitar; atualização de gráfico propaga gravação mesmo com parâmetros iguais | Carga sob demanda; medir abertura fria, preservar histórico e observações |
| Medições | T3/C | Uma string com ponto e vírgula por grupo; não cola retângulo Excel | Uma célula por medição, colagem TSV, validação e rascunhos preservados |
| Orientação | T3/C | Inferência habilitada sem perguntas sobre desenho | Perguntas sobre independência e pressupostos antes de comparar, gráfico com pontos e média/DP identificados |

Gates: pytest e Ruff. Scanners upstream ausentes, sem score. Verificação visual e nativa pendente até alterações concluídas.


Conferência intermediária: 315 testes passaram; comparação no mesmo script de processo frio PREP-003: 0,3877 s no HEAD 0.2.4 e 0,0277 s na revisão (janela Qt com processamento de eventos). Capturas de resumo/medições/gráfico a 880 px abertas, sem rolagem horizontal. Ao testar o bundle, encontrado cache Matplotlib temporário a cada execução pelo runtime hook do PyInstaller; cancelada publicação 0.2.5. 0.2.6 inclui cache estável por instalação e carregamento das fontes em tarefa de fundo. 317 testes e Ruff passaram; verificação nativa/pacotes em andamento. Banco pessoal copiado consistentemente antes da substituição, com integridade ok e dois registros existentes; sessão antiga encerrada por fechamento normal.


Inspeção nativa 0.2.6 em sessão temporária: resumo abre sem espera perceptível; colagem TSV por teclado conferida com Controle [2,4,6] e Tratamento [3,5,7], médias 4/5 e DP 2. Recolher/expandir medições durante a primeira carga de fontes respondeu imediatamente; cache fontlist gerado e análise concluída. Gráfico foi visto na janela. Encontrados três ajustes visuais finais: borda de grupos recolhidos parecia campo vazio, exportação JSON duplicada dentro/fora da análise e ponto central podia coincidir com marcador da média. Publicação 0.2.6 cancelada para corrigir esses achados antes da entrega 0.2.7.


## Screen seen — revisão final 0.2.7

| Tela | Ambiente/dados | Resultado observado |
|---|---|---|
| Resultados resumidos | Qt 880×720 e instalado Mac 1180 px, PREP-003 1,5 mg/mL, 100 mL, pureza 100% | 150 mg em destaque; parâmetros e simulação recolhidos; sem campos vazios aparentes; exportação única |
| Medições e gráfico | Qt 880 px; dois grupos com três valores cada | Tabela por célula; pontos separados da média/DP; legenda e unidades legíveis, sem rolagem horizontal |
| Entrada e análise nativa | Instalado Mac, sessão temporária | TSV colado pelo teclado, médias 4/5 e DP 2; recolher/expandir respondeu durante carga de fontes; gráfico e tabela vistos |
| Simulação nativa | Instalado 0.2.7, cache persistente da sessão anterior | Carga sob demanda solicitada, sem iniciar dependências na abertura do resumo |

Sem score, scanners upstream ou teste manual Windows. CI final e instaladores em conferência.


Conclusão 0.2.7: [CI 42551354018](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions/runs/42551354018) aprovado; Mac 317 testes, Windows 316 aprovados e um caso SQLite/diretório aberto inaplicável. Executáveis Mac/Windows e instalado Windows: ok, dez protocolos, dez POPs e média observada 4. Instalador Windows passou instalação/desinstalação com preservação de registro. Assets v0.2.7 baixados para Instaladores; ZIP conferido sem erro e plist 0.2.7. Tamanhos: Mac 78,6 MiB e instalador Windows 75,0 MiB. Instalado Mac local 0.2.7 passou verificação empacotada assíncrona, reaberto no Início; dois registros pessoais vistos e conteúdo comparado com backup consistente sem alterações. Sessões de QA isoladas dos dados reais; bundles intermediários e backups temporários de aplicativos removidos. Primeira preparação de fontes pode demorar segundos, com janela responsiva e cache reutilizado; não foi feito teste manual no PC Windows nem avaliação de usabilidade com pesquisadores.


## Estilo Bancada aprovado por Lucas — 08/11/2026

| Região | Tier/superfície | Alteração autorizada e raiz confirmada | Verificação |
|---|---|---|---|
| Shell | T2/B | Direção Bancada: navegação lateral discreta, azul, fundos sólidos, fonte do sistema; shell atual usa botões grandes e verde | Todas as etapas, foco e estado desabilitado, 880/1180 px |
| Medições | T3/C | AnalysisWidget fica escondido em grupo recolhido e abaixo de controles de cálculo | Entrada visível ao abrir Medições e análise; colagem/rascunhos/cálculo mantidos |
| Resumo | T2/B | Tabela vazia ocupa espaço e status longo torna difícil ver se funcionou | Estado vazio explícito e tabela apenas após calcular; média/DP/variância e gráfico preservados |
| Planejamento de referência | T3/C | Repetição das quantidades/ajustes acima das medições | Consulta/edição em painel secundário; invalidar observações ao editar preservado |

Sem bibliotecas novas, imagens decorativas ou animação. Gates pytest/Ruff; scanners upstream ausentes. Capturas e janela nativa pendentes nesta abertura do relatório.


## Screen seen — Bancada 0.2.8

Capturas Qt a 880 × 720, PREP-003 com 1,5 mg/mL e 100 mL: medições abertas por padrão, identificação do planejamento visível, estado vazio com instrução e tabela sem rolagem horizontal. Dados de exemplo 1,5/1,5/1,7 e 2,1/2,4/2,6 resultaram em tabela e gráfico; planejamento e simulação permanecem acessíveis em seção secundária. Uma regressão de colagem por atalho causada pela nova hierarquia de widgets foi corrigida com sinal Qt e coberta pelo teste existente de colagem. Suíte completa 317 testes e Ruff passaram em desenvolvimento. Sem score nem scanners upstream; inspeção do bundle e CI em andamento.


Conferência nativa 0.2.8: aplicativo instalado em sessão temporária, PREP-003, 1,5 mg/mL e 100 mL; tela Medições e análise aberta com entrada visível, azul discreto e planejamento associado. Fonte de sistema e widgets Qt existentes. Suíte completa de 317 testes e Ruff aprovados em desenvolvimento; executável Mac passou verificação empacotada de dez protocolos, POPs e média 4. Aplicativo real reaberto após backup consistente; conteúdo dos três registros comparado e preservado. CI de Mac/Windows em andamento; sem teste manual no Windows ou score upstream.

CI 42562090461 aprovado para Mac e Windows, incluindo teste de instalação e preservação de registro. Release 0.2.8 publicada; instaladores locais atualizados e ZIP Mac verificado. Teste manual do Windows não realizado.

## Integração de coleta e resultados — 09/11/2026 — candidata 0.2.9

Superfícies B/T2: prévia Excel (conferir colunas antes da substituição), organização da coleta (vincular unidades aos dados), mapa de microplacas (localizar amostras), medições/análise (interpretar e exportar resultados) e ajuda (entender a sequência). Ações preservam o histórico; registros arquivados continuam apenas para consulta/exportação.

### Screen seen

| Superfície | Ambiente | Dados e evidência |
|---|---|---|
| Prévia Excel | Qt offscreen 720×520 | Identificador numérico e dois grupos, três medições cada. Seleção de colunas e seis valores conferidos em `output/qa-integracao/importacao.png` |
| Mapa da coleta | Qt offscreen 850×520 | Cem unidades, duas placas de 96 poços. Primeira placa inspecionada em `output/qa-integracao/microplaca.png`; troca para segunda e posição U00097 verificadas por teste |
| Relatório Word | Renderer empacotado, quatro páginas | PREP-003, dois grupos, teste t, gráfico, observações, parâmetros, procedimento e fontes. Todas as páginas inspecionadas em `output/qa-relatorio/render-final-graph/` |
| Janela nativa integrada | Pendente | Mac bloqueado; CUA não conseguiu acessar a janela. Não equivale às capturas offscreen |

Correções confirmadas: comparação em JSON substituída por texto interpretável; números do relatório formatados sem alterar dados numéricos Excel/CSV; cabeçalhos repetidos nas tabelas; gráfico incluído no relatório; páginas de oito grupos no gráfico para evitar rótulos sobrepostos; importação não aloca uma matriz gigante de células vazias; ajuda acessível na navegação. Cada página gráfica permanece identificada e o Word inclui todas; PNG exporta a página selecionada.

Ruff aprovado e 349 testes aprovados no macOS, sem falhas ou testes pulados. Smoke do bundle Mac passou com dez POPs, cálculo, média, modelo Excel/importação conferida e três exportações. A recompilação após os últimos ajustes de proveniência e a distribuição Windows ainda precisam de evidências finais. Gates upstream indisponíveis continuam não executados; sem nota inventada. Não representa avaliação com pesquisadores ou validação em bancada.

Atualização final de testes: 351 casos aprovados localmente, sem pulos/falhas/erros. O CI do código de execução passou em Mac (349 casos) e Windows (349 casos, um pulo por restrição do SO a mover diretório SQLite aberto), mais smoke do bundle e instalação/desinstalação. Os dois testes adicionais só ampliam cobertura; não alteram execução. Conferência nativa do novo fluxo continua pendente pelo bloqueio do Mac.
