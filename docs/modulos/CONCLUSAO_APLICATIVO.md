# Critérios de conclusão do aplicativo — autorização de 09/11/2026

Lucas autorizou concluir o produto atual, deixando apenas a ampliação do catálogo de protocolos para depois. A entrega inclui preparos/diluições e organização de ensaios, sem escolher um único caso como substituto do escopo.

| Área | Critério verificável | Estado atual |
|---|---|---|
| Protocolos atuais | Dez PREP, cálculo, entradas/unidades, fonte, POP/DOCX | Implementado; regressões e dez POPs conferidos |
| Organização experimental | Controles, tratamentos, unidades independentes, repetições e organização em recipientes/microplacas ligados ao plano | Implementado; controle/tipo de repetição, mapa e posições testados; inspeção nativa pendente |
| Excel | Importação por arquivo, múltiplos formatos/abas, prévia, erros claros, leitura em segundo plano | Implementado e testado em três formatos, com mapeamento; diálogo nativo pendente |
| Modelo de coleta | Planilha gerada pelo planejamento com identificadores e espaços vazios para medições reais | Modelo vazio, manifesto e retomada testados de ponta a ponta |
| Vínculo | Conferir correspondência entre coleta/importação e organização planejada, preservar proveniência | Manifesto, amostras, grupos e contagens conferidos antes da substituição |
| Estatística básica | Média, DP, variância, t/ANOVA com desenho e pressupostos explícitos; resultados indefinidos tratados | Testes, limites, ajuda e resultados analíticos independentes conferidos |
| Gráficos | Dados observados identificados, legíveis, exportáveis, sem confundir com simulação | Gráficos de oito grupos por página; PNG e todas as páginas no Word |
| Exportações | Dados e resumo em Excel/CSV, relatório do experimento com parâmetros, fontes e análise; figuras | Formatos testados; relatório com gráfico de quatro páginas inspecionado; gravação atômica |
| Continuidade | Preservar rascunhos, histórico, importações e exportações; recuperação/backup verificáveis | Retomada recente e proveniência testadas; arquivos somente consulta/exportação; instalação preservada |
| Interface | Estilo Bancada, ajuda contextual, estados vazios/erro/sucesso e teclado; nenhuma etapa pareça indisponível sem motivo | Bancada, ajuda e diálogos inspecionados offscreen; janela nativa pendente pelo Mac bloqueado |
| Distribuição | Mac instalado e verificado; instalador Windows e preservação de registros testados; downloads atualizados | Pacotes 0.2.9 e instalador Windows aprovados no CI; atualização instalada/publicação final pendentes |

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
