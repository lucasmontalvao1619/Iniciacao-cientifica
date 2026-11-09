# Critérios de conclusão do aplicativo — autorização de 09/11/2026

Lucas autorizou concluir o produto atual, deixando apenas a ampliação do catálogo de protocolos para depois. A entrega inclui preparos/diluições e organização de ensaios, sem escolher um único caso como substituto do escopo.

| Área | Critério verificável | Estado atual |
|---|---|---|
| Protocolos atuais | Dez PREP, cálculo, entradas/unidades, fonte, POP/DOCX | Implementado, reconferir regressões |
| Organização experimental | Controles, tratamentos, unidades independentes, repetições e organização em recipientes/microplacas ligados ao plano | Controle e tipo de repetição registrados na coleta; conferir fluxo completo e visualização |
| Excel | Importação por arquivo, múltiplos formatos/abas, prévia, erros claros, leitura em segundo plano | Leitura/prévia e leitura em segundo plano implementadas; conferir integração nativa |
| Modelo de coleta | Planilha gerada pelo planejamento com identificadores e espaços vazios para medições reais | Gerador e interface implementados; conferir persistência/vínculo |
| Vínculo | Conferir correspondência entre coleta/importação e organização planejada, preservar proveniência | Implementado manifesto com registro/hash do plano e amostras; ampliar integração/UI |
| Estatística básica | Média, DP, variância, t/ANOVA com desenho e pressupostos explícitos; resultados indefinidos tratados | Existente; ampliar conferência e orientação |
| Gráficos | Dados observados identificados, legíveis, exportáveis, sem confundir com simulação | Existente; conferir seleção e exportação |
| Exportações | Dados e resumo em Excel/CSV, relatório do experimento com parâmetros, fontes e análise; figuras | Excel/CSV/Word com plano, parâmetros e fontes; falta QA visual do relatório |
| Continuidade | Preservar rascunhos, histórico, importações e exportações; recuperação/backup verificáveis | Retomada de registros recentes com coleta/proveniência implementada e testada; arquivos seguem consulta; conferir interface nativa |
| Interface | Estilo Bancada, ajuda contextual, estados vazios/erro/sucesso e teclado; nenhuma etapa pareça indisponível sem motivo | Conferir após integração |
| Distribuição | Mac instalado e verificado; instalador Windows e preservação de registros testados; downloads atualizados | Recompilar ao concluir |

Conclusão exige execução integrada, inspeção de telas e evidências por item. Não declarar que testes computacionais substituem avaliação de usabilidade, validação em bancada ou aprovação científica. Não adicionar novos protocolos durante esta entrega. Não ampliar para técnicas estatísticas sem limite: o escopo estatístico obrigatório é o do projeto (descritiva, t e ANOVA); desenhos incompatíveis devem ser identificados e encaminhados com clareza.

## Conferência de 09/11/2026 — candidata 0.2.9

Implementados e verificados em testes: mapeamento de cabeçalho/colunas Excel, prevenção de identificadores numéricos como grupos, manifesto de coleta vinculado ao registro/plano, retomada recente, mapa consultável de microplacas, bloqueio de comparação para repetições técnicas, gráficos paginados com todos os grupos no relatório, exportações Excel/CSV/Word e gravação atômica para preservar arquivo anterior em falha. Importação e análise usam trabalhadores em segundo plano; rascunhos e fontes permanecem vinculados ao planejamento.

349 testes passaram localmente, sem falhas/pulos; Ruff aprovado. Relatório com gráfico renderizado e quatro páginas inspecionadas; diálogos de importação e microplaca inspecionados em Qt offscreen. Fonte de evidências e limites em `docs/interface/AUDIT.md`.

**Ainda não declarar conclusão:** falta a conferência da versão final na janela nativa (Mac bloqueado), substituir com segurança o aplicativo instalado, concluir pipeline Windows/Mac e atualizar os downloads locais/publicados. O aplicativo instalado permanece 0.2.8 até a troca segura. Nenhum protocolo novo foi adicionado. Testes computacionais não demonstram usabilidade, redução de tempo/erros ou validação em bancada.
