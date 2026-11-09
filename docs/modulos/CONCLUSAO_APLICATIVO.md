# Critérios de conclusão do aplicativo — autorização de 09/11/2026

Lucas autorizou concluir o produto atual, deixando apenas a ampliação do catálogo de protocolos para depois. A entrega inclui preparos/diluições e organização de ensaios, sem escolher um único caso como substituto do escopo.

**Estado atual: entrega funcional 0.2.9 concluída em 09/11/2026.** O quadro abaixo resume a situação vigente; as seções posteriores preservam o histórico das conferências e bloqueios já resolvidos.

| Área | Critério verificável | Estado atual |
|---|---|---|
| Protocolos atuais | Dez PREP, cálculo, entradas/unidades, fonte, POP/DOCX | Implementado; regressões e dez POPs conferidos |
| Organização experimental | Controles, tratamentos, unidades independentes, repetições e organização em recipientes/microplacas ligados ao plano | Implementado; modelo e mapa conferidos no executável; restauração de geometria corrigida e testada nos seis tamanhos |
| Excel | Importação por arquivo, múltiplos formatos/abas, prévia, erros claros, leitura em segundo plano | Três formatos/mapeamento testados; importação externa e do próprio modelo conferidas no executável |
| Modelo de coleta | Planilha gerada pelo planejamento com identificadores e espaços vazios para medições reais | Modelo vazio, manifesto e retomada testados de ponta a ponta |
| Vínculo | Conferir correspondência entre coleta/importação e organização planejada, preservar proveniência | Manifesto, amostras, grupos e contagens conferidos antes da substituição |
| Estatística básica | Média, DP, variância, t/ANOVA com desenho e pressupostos explícitos; resultados indefinidos tratados | Testes, limites, ajuda e resultados analíticos independentes conferidos |
| Gráficos | Dados observados identificados, legíveis, exportáveis, sem confundir com simulação | Gráficos de oito grupos por página; PNG e todas as páginas no Word |
| Exportações | Dados e resumo em Excel/CSV, relatório do experimento com parâmetros, fontes e análise; figuras | Formatos testados; relatório com gráfico de quatro páginas inspecionado; gravação atômica |
| Continuidade | Preservar rascunhos, histórico, importações e exportações; recuperação/backup verificáveis | Retomada recente e proveniência testadas; arquivos somente consulta/exportação; instalação preservada |
| Interface | Estilo Bancada, ajuda contextual, estados vazios/erro/sucesso e teclado; nenhuma etapa pareça indisponível sem motivo | Bancada, ajuda, histórico legível, Excel, mapa e resultados inspecionados na janela nativa; teclado conferido no histórico e número de repetições |
| Distribuição | Mac instalado e verificado; instalador Windows e preservação de registros testados; downloads atualizados | 0.2.9 instalada/aberta no Mac; tag publicada, CI Mac/Windows aprovado; instaladores locais iguais aos publicados por SHA-256 |

Conclusão exige execução integrada, inspeção de telas e evidências por item. Não declarar que testes computacionais substituem avaliação de usabilidade, validação em bancada ou aprovação científica. Não adicionar novos protocolos durante esta entrega. Não ampliar para técnicas estatísticas sem limite: o escopo estatístico obrigatório é o do projeto (descritiva, t e ANOVA); desenhos incompatíveis devem ser identificados e encaminhados com clareza.

## Conferência de 09/11/2026 — candidata 0.2.9

Implementados e verificados em testes: mapeamento de cabeçalho/colunas Excel, prevenção de identificadores numéricos como grupos, manifesto de coleta vinculado ao registro/plano, retomada recente, mapa consultável de microplacas, bloqueio de comparação para repetições técnicas, gráficos paginados com todos os grupos no relatório, exportações Excel/CSV/Word e gravação atômica para preservar arquivo anterior em falha. Importação e análise usam trabalhadores em segundo plano; rascunhos e fontes permanecem vinculados ao planejamento.

349 testes passaram localmente, sem falhas/pulos; Ruff aprovado. Relatório com gráfico renderizado e quatro páginas inspecionadas; diálogos de importação e microplaca inspecionados em Qt offscreen. Fonte de evidências e limites em `docs/interface/AUDIT.md`.

**Ainda não declarar conclusão:** falta a conferência da versão final na janela nativa (Mac bloqueado), substituir com segurança o aplicativo instalado, concluir pipeline Windows/Mac e atualizar os downloads locais/publicados. O aplicativo instalado permanece 0.2.8 até a troca segura. Nenhum protocolo novo foi adicionado. Testes computacionais não demonstram usabilidade, redução de tempo/erros ou validação em bancada.


Conferência independente adicional: teste t com variância amostral 4 e erro padrão da diferença √(8/3); ANOVA com somas de quadrados entre 54/dentro 6, F(2,6)=27 e p=0,001 por expressão analítica da distribuição. Teste numérico dirigido aprovado, sem usar a chamada SciPy como resultado esperado.

Bundle Mac final recompilado com assinatura ad hoc verificada na origem temporária. Smoke completo aprovado em `/tmp/planejador-029-final-smoke.json`. A montagem do ZIP dentro do Desktop encontrou metadados de provedor de arquivos na cópia; não substitui nem invalida a verificação do bundle temporário. Pacotes do CI são montados em ambiente limpo e serão conferidos separadamente.

## Pacotes aprovados no CI — 09/11/2026

[Execução 42567226528](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions/runs/42567226528): Mac e Windows aprovados. Os dois testaram 349 casos do commit de implementação `015f643`; Mac sem pulos, Windows com um pulo explícito porque o sistema impede mover diretório com SQLite aberto. Sem falhas/erros. Executáveis verificaram cálculo, média observada, dez POPs, modelo/importação Excel e três exportações. Instalador Windows instalado/executado/desinstalado com preservação do arquivo experimental de teste.

Após o commit de implementação foram acrescentados somente testes/documentação: conferência inferencial por resultado analítico e importação de 10.000 medições. **Suíte local final: 351 testes, nenhum pulo/falha/erro, 17,834 segundos.** Ruff aprovado. Código de execução idêntico ao validado no CI.

Artefato Mac do CI conferido: 82.908.450 bytes, CRC aprovado, versão 0.2.9, catálogo idêntico ao código, dez POPs e ausência de bancos de usuário. ZIP local montado em pasta temporária também conferido: 83.460.351 bytes; diferenças de runtime/compactação não são dados de pesquisador. A cópia temporária evita os metadados do provedor do Desktop que interromperam a montagem local direta.

Permanece pendente a conferência visual na janela nativa e a troca segura da instalação 0.2.8 enquanto o Mac está bloqueado. O pedido de desbloqueio foi enviado; não houve confirmação de desbloqueio. Antes da troca foi registrada localmente uma assinatura dos conteúdos dos **quatro registros** atuais, sem publicar esses conteúdos. Não substituir o aplicativo em uso nem inventar uma conferência visual.

Distribuição preparada como **rascunho v0.2.9** no GitHub, ainda sem alterar a última versão pública: [rascunho](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/releases/tag/untagged-965aa33955a414fa3afa). Três assets confirmados como uploaded: Mac 82.908.450 bytes; instalador Windows 79.138.717 bytes; portátil Windows 116.180.766 bytes. ZIPs com CRC aprovado e dez POPs; instalador com cabeçalho PE e execução aprovada pelo CI. Não substituir cópias visíveis em Instaladores antes de publicar/alinhar a instalação local, para evitar versões apresentadas como iguais.

Próxima ação depende de desbloqueio do Mac: inspecionar a janela isolada `Planejador — conferência isolada`, fechar a sessão de teste e o aplicativo de produção normalmente, fazer backup SQLite consistente, instalar o bundle 0.2.9, conferir fluxo nativo com dados separados, reabrir produção sem variável de teste e comparar a assinatura dos quatro registros. Só então publicar o rascunho, atualizar Mac.zip/Windows-Setup.exe em Instaladores e encerrar a meta. Não há autorização pendente para essas ações; falta acesso à tela desbloqueada. Se a inspeção revelar defeitos, corrigir e repetir somente os checks afetados antes de publicar.


## Conferência nativa e dados preservados — 09/11/2026

Mac desbloqueado após resposta de Lucas. Sessões antigas fechadas normalmente, com flush dos rascunhos; backup SQLite consistente em `Pesquisa/backups-dados/antes-integracao-029-20261109.sqlite3`, fora do repositório público. Quatro registros pessoais mantiveram a mesma assinatura de conteúdo após substituir somente o bundle e reabrir pelo atalho do Desktop. Nenhum dado de teste foi incluído no histórico pessoal.

No executável, usando diretório separado: retomada recente; importação externa com Controle [2,4,6] e Tratamento [3,5,7]; médias 4 e 5/DP 2; exportação Excel conferida; relatório Word gerado com figura; modelo Excel com seis valores vazios e IDs A1–A6; preenchimento de observações de teste e reimportação validada pelo manifesto; mapa de 96 poços e guia de uso abertos. O relatório de quatro páginas já havia sido renderizado e inspecionado página por página. A consulta do histórico passou a mostrar texto legível, mantendo JSON integral na exportação.

Defeito confirmado e corrigido na inspeção: Qt não reencontrava a tupla de geometria no seletor, restaurando 6 em vez de 96 poços. Agora compara as dimensões explicitamente; testes cobrem os seis formatos e o executável final voltou a mostrar **96 poços (8 × 12)** ao reabrir. Grupos importados e contagens são reaproveitados; limite de coleta alinhado a 10.000 unidades totais, sem truncar contagens de importação. Originais dos dez POPs preservados: todas as partes internas dos DOCX são idênticas às do pacote; apenas metadados do contêiner ZIP diferem.

Código final: `bfb1abfa7902332c7f8c450065de46265ceb185d`. **361 testes locais aprovados**, Ruff aprovado; [CI de implementação 42625202601](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions/runs/42625202601) aprovado em Mac/Windows, incluindo smoke/instalador. Windows tem um pulo por restrição do SO a mover diretório SQLite aberto; não há falhas. A publicação `v0.2.9` aponta para esse commit e disparou o pipeline da tag; conferir sua conclusão e os assets antes de encerrar a meta.

Limites de avaliação: não houve teste manual no PC Windows do pesquisador, avaliação formal de usabilidade ou validação em bancada. A verificação Windows foi executada em ambiente Windows nativo do GitHub. Isso limita as afirmações científicas; não impede a entrega do escopo funcional documentado. Nenhum protocolo adicional foi criado nesta entrega.


## Encerramento da entrega 0.2.9

[Release pública](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/releases/tag/v0.2.9) e [pipeline da tag 42627055044](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions/runs/42627055044) aprovados, incluindo publicação automática. A última versão pública é 0.2.9, sem marca de rascunho/prévia; tag no commit bfb1abf. Os links Windows/Mac da página inicial apontam para os pacotes atuais.

`Instaladores/Planejador-Mac.zip` (82.909.088 bytes) e `Instaladores/Planejador-Windows-Setup.exe` (79.142.606 bytes) foram baixados da release e conferidos com os SHA-256 do GitHub. Mac: `47ad35bd7b1e0b8844707a0b29ad0c29979a85dfb7cc8044c001936f806d32d4`; Windows Setup: `bf822e40a4241b638d1eb26fc98c728823ed3c6ba3037c19d61dff15d1e989eb`. ZIP portátil Windows permanece somente no GitHub. CRC, versão, catálogo idêntico ao código, dez POPs e ausência de bancos pessoais conferidos no ZIP Mac. Os pacotes Windows passaram na compilação/teste/instalação/desinstalação nativos do CI.

A instalação pessoal deriva do mesmo commit final bfb1abf aprovado no CI e foi inspecionada na janela nativa. O app está aberto em Início com os quatro registros originais; assinatura do conteúdo antes/depois idêntica. Backup SQLite consistente preservado, bem como fontes científicas, originais e os dez POPs. Rollbacks temporários de aplicativos usados nesta atualização foram removidos. Nenhum dado real foi substituído por simulações.

Todos os critérios funcionais do quadro possuem evidência em testes, arquivos, renderizações ou execução nativa descritos acima. Nenhum trabalho obrigatório de implementação/distribuição desta versão permanece pendente. A ampliação do catálogo fica para depois, conforme Lucas. Avaliação formal com pesquisadores, validação em bancada e resultados dos artigos continuam atividades científicas futuras; não foram inventadas nem declaradas realizadas.
