# Entrega dos dez protocolos PREP

Escopo solicitado por Lucas em 08/11/2026; execução sequencial, preservando os dez itens atuais. Estado não equivale a resultado validado.

| Exigência | Evidência necessária | Situação |
|---|---|---|
| PREP-001 a PREP-010 funcionais | Fórmulas e limites por fonte/página, core e testes independentes, parâmetros próprios | PREP-001 a PREP-009 implementados; PREP-010 pendente |
| POP individual e DOCX com imagens | Conteúdo por protocolo, fonte técnica, crédito/licença/data da imagem, renderização verificada | PREP-001 e PREP-002 com DOCX ilustrado conferido em duas páginas cada; PREP-003 e PREP-005 em três páginas, PREP-004, PREP-006, PREP-007, PREP-008 e PREP-009 em duas; PREP-010 pendente |
| Resultados e gráficos aplicáveis | Fluxo executado por protocolo, edição ao vivo sem misturar medições | PREP-001 a PREP-009 implementados e testados |
| Histórico de dez | Persistência após reiniciar, arquivamento de excedentes e exclusões para consulta/exportação | Implementado e testado com persistência e falha de gravação |
| Remover linguagem de prévia | Inspeção da interface e exportações, estados honestos de implantação | Interface ativa e POP atualizados; relatórios históricos preservados |
| Windows nativo e Mac | Builds, ZIP com Registros de Experimentos e testes reais em cada sistema | Receita Windows preparada; execução adiada por Lucas até ter PC disponível |
| Proveniência | REGISTRO.md e fichas com origem/edição/página/horário real | Consulta inicial Fiocruz registrada |

Recorte metodológico confirmado; históricos arquivados somente para consulta/exportação. Não existe autorização para alegar validação de bancada nem incluir automaticamente fontes na revisão.

Entrega incremental verificável: 117 testes passaram na suíte completa; após ajustes numéricos, 22 testes de cálculo/histórico passaram novamente. Ruff e diff --check sem erros. Tipagem dos três módulos novos passou com `--follow-imports=skip`; a checagem com dependências encontrou erro de sintaxe nos stubs PyQt6/QtGui, portanto não é registrada como tipagem completa aprovada.

Mac: bundle reconstruído e assinatura verificada no diretório temporário, Desktop atualizado sem encerrar sessão em uso. `output/distribuicao/Planejador-Mac-PREP-001.zip` conferido por CRC e conteúdo: app, POP e pasta de registros. Fluxo, gráfico e histórico inspecionados em Qt de desenvolvimento; cliques no bundle não foram revalidados. Próximo protocolo: PREP-003, com revisão do escopo de solução-estoque e sua identificação/estabilidade antes da liberação. O objetivo dos dez continua em andamento.

PREP-002: 139 testes passaram na suíte completa. Módulos core/service alterados passaram na verificação tipada com imports omitidos. A infraestrutura Qt de parâmetros/resultados foi compartilhada entre os dois tipos, em frontend/preparos.py, com teste de troca de protocolo e de edição ao vivo. Nenhum resultado observado foi fabricado. Receita Windows permanece preparada para execução posterior, conforme decisão de Lucas.

Entrega atual de PREP-002: `output/distribuicao/Planejador-Mac-PREP-001-002.zip` com ambos os protocolos/POPs e pasta de registros, assinatura e integridade verificadas. Aplicativo em uso no Desktop não substituído; fechar antes de instalar o pacote. A inspeção desta entrega foi em Qt de desenvolvimento e no DOCX renderizado, sem novos cliques na cópia empacotada.


Entrega PREP-003 em 08/11/2026: perguntas condicionais para estoque, teor, potência/atividade e equivalência específica; dados de rótulo opcionais. 165 testes passaram na suíte completa; Ruff e diff --check sem erros. Core/service passaram em mypy com imports omitidos (limite de stubs Qt preservado). Capturas Qt dos parâmetros e resultados e DOCX de três páginas inspecionados. Detectados e corrigidos largura excessiva e corte do texto após redimensionar; teste impede regressão na janela mínima de 880 px.

`output/distribuicao/Planejador-Mac-PREP-001-a-003.zip` inclui aplicativo, três POPs e Registros de Experimentos. Assinatura local, recursos, catálogo e CRC conferidos. A sessão Desktop em uso não foi substituída. Fluxo verificado em Qt de desenvolvimento, sem novos cliques na cópia empacotada; Windows continua adiado conforme escolha de Lucas. Próxima entrega: PREP-004, diluição de solução-estoque. Sete protocolos ainda pendentes.


PREP-004: implementada diluição volumétrica com unidade comum por volume, alíquota/fator e diluente q.s.p. Reutiliza preparar_diluicao do núcleo existente; entradas não finitas e resultados fora da faixa são rejeitados. 181 testes passaram na suíte completa, Ruff e mypy dos módulos alterados com imports omitidos aprovados; não é checagem tipada completa das dependências. Inspeção das capturas Qt e das duas páginas do DOCX. Restam seis protocolos; próxima entrega PREP-005, diluição seriada/sucessiva.


Pacote PREP-001 a PREP-004: `output/distribuicao/Planejador-Mac-PREP-001-a-004.zip`, com aplicativo, quatro POPs e pasta Registros de Experimentos. Assinatura local, catálogo empacotado, imagens e CRC do ZIP conferidos. A sessão Desktop em uso não foi substituída. A inspeção do fluxo foi em Qt de desenvolvimento; não foram repetidos cliques no bundle. Windows continua com compilação/teste adiado conforme decisão de Lucas.


PREP-005: série volumétrica de fator constante com perguntas específicas, tabela e gráfico logarítmico editáveis. Volumes preparados e remanescentes distintos; retirada do último para igualar volumes é escolha explícita. 202 testes passaram, com balanços de volume/soluto e desenho do gráfico em faixa numérica extrema; Ruff aprovado, mypy core/service com imports omitidos aprovado (sem tipagem completa de dependências). DOCX ilustrado inspecionado em três páginas. Ficha e REGISTRO preservam divergências bibliográficas do volume 4, sem ISBN ou edição inventados. Próximo protocolo: PREP-006. Cinco ainda pendentes.


Pacote Mac PREP-001 a PREP-005: `output/distribuicao/Planejador-Mac-PREP-001-a-005.zip`, com aplicativo, cinco POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Ajuste final de margens do gráfico seguido por 19 testes de interface aprovados. Sessão Desktop preservada; fluxo conferido em Qt de desenvolvimento, sem novos cliques no pacote. Windows permanece preparado para execução posterior, conforme escolha de Lucas.


PREP-006: fator e concentração final a partir de C1, V1 e V2; perguntas específicas, gráfico de C2 por V2 com C1/V1 fixos e ponto do preparo. 219 testes passaram; Ruff e mypy core/service com imports omitidos aprovados, sem alegar tipagem completa. DOCX ilustrado inspecionado em duas páginas e capturas Qt conferidas. Fonte Fiocruz p. 230–232, consulta registrada e derivações explícitas. Próximo protocolo PREP-007; quatro pendentes.


Pacote Mac PREP-001 a PREP-006: `output/distribuicao/Planejador-Mac-PREP-001-a-006.zip`, com aplicativo, seis POPs e pasta Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows continua com compilação/teste preparado para execução posterior no PC, conforme escolha de Lucas.


PREP-007: dimensionamento de volume base/reserva/total, percentual escolhido pelo pesquisador, sem margem positiva automática. Gráfico comparativo editável com no máximo 21 pontos; unidades explícitas e contagem já incluindo controles/repetições. Fonte integral MS 2016 da BVS, p. 48, adaptação percentual explícita. 237 testes passaram; Ruff e mypy core/service com imports omitidos aprovados. POP de duas páginas com nova foto creditada e capturas Qt conferidos. Próximo protocolo PREP-008; três pendentes.


Pacote Mac PREP-001 a PREP-007: `output/distribuicao/Planejador-Mac-PREP-001-a-007.zip`, com aplicativo, sete POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, três imagens de equipamentos e CRC conferidos. Após o ajuste final do texto explicativo, 153 testes de cálculo/interface passaram novamente. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows permanece preparado para compilação/teste posterior no PC, conforme escolha de Lucas.


PREP-008: escala de formulação, receita Anvisa identificada/protegida e autoria do pesquisador separada. Componentes e condições perguntados conforme origem; ciclo não presumido, conservação da referência identificada sem validade automática. Tabela e gráfico editáveis por componente, preservando unidades e pendências. 251 testes passaram; Ruff e mypy core/service com imports omitidos aprovados. Capturas Qt e POP de duas páginas inspecionados; corte na tabela e créditos órfãos do DOCX corrigidos. Fonte Anvisa p. 14–15, consultas e imagem registradas. Restam PREP-009 e PREP-010.


Pacote Mac PREP-001 a PREP-008: `output/distribuicao/Planejador-Mac-PREP-001-a-008.zip`, com aplicativo, oito POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Módulo frontend.formulacao confirmado no arquivo PYZ; teste do fluxo de formulação passou novamente após ajuste final da altura das linhas. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows permanece preparado para compilação/teste posterior no PC, conforme escolha de Lucas.

Integração final ainda a conferir: os Resultados dos PREP exibem dimensionamento planejado. O módulo existente de medições/estatística não está conectado a esses painéis; não declarar o fluxo completo de análise observacional atendido sem resolver essa integração e verificar persistência/exportação das medições, preservando a separação entre planejado e observado.


PREP-009: proporção do fabricante declarada, volume de água/final escolhido explicitamente, massa dimensionada e gráfico editável. Fonte técnica Anvisa separada da instrução particular informada pelo pesquisador; condições faltantes permanecem pendentes. 265 testes passaram, Ruff e mypy service com imports omitidos aprovados. Fonte e consulta registradas, capturas Qt e duas páginas do POP inspecionadas. Resta PREP-010 e integração final de medições/estatística, exportações e comprovação do estado completo; não confundir dimensionamento com observações.


Pacote Mac PREP-001 a PREP-009: `output/distribuicao/Planejador-Mac-PREP-001-a-009.zip`, com aplicativo, nove POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Módulo frontend.meio_comercial confirmado no PYZ. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows permanece preparado para compilação/teste posterior no PC, conforme escolha de Lucas.

Pendência metodológica prioritária após esclarecimento de Lucas em 08/11/2026: regularizar os livros Fiocruz usados nos PREP-001 a PREP-006, cuja obtenção foi direta na EPSJV/IOC. Confirmar registro/cópia em um dos oito portais permitidos ou substituir as fontes com conferência das regras. Não declarar esses itens conformes ao recorte de procedência enquanto isso não estiver comprovado. Ver decisão registrada em docs/decisoes/README.md.


## Regularização confirmada — 2026-11-08T10:43:13.707165-03:00

Pendência de procedência dos PREP-001 a PREP-006 resolvida: downloads efetivos dos volumes 1 e 4 no Arca, comparados byte a byte com as cópias anteriores. Catálogo identifica novos acessos sem apagar os antigos. Ver [evidências e limites](../referencias/REGULARIZACAO_FONTES.md). A inclusão formal e a edição mais recente continuam sem comprovação; divergência bibliográfica do volume 4 preservada.

Verificação desta atualização: 265 testes passaram (um aviso preexistente Starlette/httpx), Ruff e `git diff --check` aprovados. Os seis POPs alterados foram renderizados e todas as 14 páginas inspecionadas. Cálculos e páginas das fontes mantidos por identidade dos PDFs.


Regularização de fontes concluída: pacote `output/distribuicao/Planejador-Mac-PREP-001-a-009-fontes-regularizadas.zip` (82.720.131 bytes), com catálogo atualizado, nove POPs e pasta de registros. Assinatura ad hoc, igualdade do catálogo empacotado, CRC e presença dos nove POPs conferidos. Sessão Desktop e dados existentes preservados; sem repetir cliques no bundle ou testes Windows. Fonte regularizada não equivale à inclusão formal ou comprovação da edição mais recente.


## PREP-010 implementado — 08/11/2026

Dimensionamento de meio para placas ou tubos, dose, unidade, contagem já incluindo controles/repetições e excedente escolhido. Formato/capacidade e método declarados separadamente, ausências pendentes. Um tipo de recipiente e uma dose por planejamento; sem dose universal, massa de pó ou condições automáticas. Fontes Anvisa p. 18 (PDF 20) e BVS MS p. 48 (PDF 49), horários/hashes e adaptação registrados. Gráfico por número de recipientes com edição ao vivo, mesmo histórico e exportação JSON com proveniência.

280 testes passaram, Ruff aprovado e mypy do service com imports omitidos aprovado (não equivale a tipagem completa das dependências). Capturas Qt a 880 px e gráfico inspecionados; sem rolagem horizontal da página. POP ilustrado renderizado em três páginas e integralmente inspecionado; corrigida no exportador comum a separação entre imagem e créditos. Não houve teste de leitor de tela ou validação em bancada.

Os dez PREP têm dimensionamento, perguntas e POP individuais. A integração final de medições observadas/estatística ao fluxo desses protocolos ainda falta; não confundir seus gráficos de dimensionamento com análise de observações. Windows continua preparado para compilação/teste posterior no PC, conforme decisão de Lucas.


Pacote Mac PREP-001 a PREP-010: `output/distribuicao/Planejador-Mac-PREP-001-a-010.zip` (82.892.217 bytes), aplicativo, dez POPs e pasta de registros. Assinatura ad hoc, igualdade do catálogo empacotado, dez fichas com cálculo/fontes/imagem, recursos de equipamento e CRC do ZIP aprovados; sem banco de dados de usuário no pacote. Sessão Desktop preservada. Fluxo Qt de desenvolvimento inspecionado; sem repetir cliques no bundle ou testar Windows. Próxima entrega: integrar medições/estatística e exportações ao fluxo real dos dez protocolos, mantendo planejado e observado distintos.

Preparação Windows ajustada para gerar também os dez POPs ilustrados dentro do ZIP, reutilizando o exportador da aplicação; erros interrompem o empacotamento. Trecho Python teve sintaxe conferida. PowerShell, executável e documentos gerados no Windows continuam sem execução/teste nesse sistema.


## Integração de medições — 2026-11-08T11:07:39.590797-03:00

Medições observadas e estatística agora integradas aos dez PREP, no mesmo fluxo de Resultados e no histórico. Evidências, formato de persistência e limites em [análise estatística](analise-estatistica.md). A auditoria final e o teste Windows permanecem pendentes.


Pacote com medições integradas: `output/distribuicao/Planejador-Mac-PREP-001-a-010-integrado.zip` (82.894.936 bytes). Aplicativo, dez POPs e pasta de registros; assinatura ad hoc, catálogo idêntico ao código, presença da nova integração no PYZ e CRC verificados. Nenhum banco de usuário incluído. Sessão Desktop preservada; cliques no novo bundle e compilação/teste Windows ainda não realizados.


## Preservação de gravação — 2026-11-08T11:21:55.089869-03:00

Proteção de dados pendentes corrigida e testada; ver [análise estatística](analise-estatistica.md). A [conferência da entrega](CONFERENCIA_ENTREGA.md) identifica o que está comprovado e as pendências nativas/bibliográficas.


Conferência bibliográfica dirigida em 08/11/2026: cinco obras identificadas, PDFs Anvisa/BVS atuais idênticos por hash e registros Arca atuais com os mesmos bitstreams. Corrigida a edição informada do módulo 5; não localizada edição posterior do mesmo título/volume nesse escopo, sem alegar revisão formal completa. Cinco testes de interface/exportação passaram; os três POPs alterados foram renderizados e as sete páginas inspecionadas. Detalhes em [regularização das fontes](../referencias/REGULARIZACAO_FONTES.md).
