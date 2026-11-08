# Organização local da iniciação científica

Organizada em 08/11/2026 por solicitação de Lucas. Entrada única: `~/Desktop/INICIACAO CIENTIFICA`.

| Item visível | Uso |
|---|---|
| Planejador de Experimentos | Abrir o aplicativo atual, versão 0.2.1 |
| POPs | Dez procedimentos ilustrados em DOCX |
| Registros de Experimentos | Arquivos experimentais para consulta e exportação |
| Pesquisa | Acervo original, extrações, referências, notas e áreas Git/Orca preservadas |
| Instaladores | Somente Mac ZIP e instalador Windows da versão atual |
| Desenvolvimento | Código-fonte, testes e documentação técnica; não é necessário para usar |
| LEIA-ME.txt | Instruções curtas para o pesquisador |

A instalação real fica em `.aplicativo.nosync/`; a base pessoal, em `.dados/`. Atalhos antigos de dados, acervo e Orca foram redirecionados à pasta central, sem multiplicar conteúdo. O ambiente `.venv` foi conservado e seus scripts/mapas editáveis atualizados após a mudança de caminho. O repositório Git mantém sua estrutura interna e histórico.

Removidos 3.90 GiB de artefatos gerados: aplicativos 0.1.0, builds, ZIPs intermediários, caches e cópias temporárias de compilação. Quatro Markdown exportados foram removidos somente após igualdade byte a byte com seus originais; notas diferentes foram preservadas. PDFs, extrações, acervo com alterações não commitadas, fontes, dados e backups de dados mantidos. Manifesto detalhado local: `output/organizacao/20261108.json`.

As pastas de bibliotecas dentro do aplicativo/ZIP são dependências do Python, Qt, cálculos, gráficos e DOCX, incluindo links internos do PyInstaller; não foram eliminadas por parecerem duplicadas. O ZIP publicado tem aplicativo, dez POPs, pasta de registros e instruções, sem código de desenvolvimento ou dados pessoais. O texto de versão do empacotador agora vem de `pyproject.toml`, evitando o rótulo 0.2.0 fixo em versões futuras.

Conferência: 297 testes e lint passaram após mover o código; bases e acervo conferidos antes/depois por hashes no processo de mudança; área Git e worktrees continuam acessíveis pelos caminhos compatíveis. A verificação do executável instalado usa dados descartáveis, sem modificar experimentos pessoais. Esta reorganização não remove funções nem constitui nova validação em bancada.
