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
