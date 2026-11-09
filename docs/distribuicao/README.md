# Distribuição do aplicativo

## Instalação atual pelo GitHub

- Windows: baixar `Planejador-Windows-Setup.exe` na [última versão](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/releases/latest), abrir e concluir a instalação. Python não é necessário; instalação por usuário, sem exigir administrador, com atalhos. Também há ZIP portátil.
- Mac Apple Silicon: baixar `Planejador-Mac.zip`, extrair e abrir o `.app`.
- A instalação inclui os dez POPs. Dados de experimentos não são distribuídos; arquivos criados pelo pesquisador não são removidos pelo desinstalador.

O workflow `.github/workflows/desktop.yml` testa em Windows e Mac a cada alteração na main e PR; tags `v*` publicam os pacotes somente após testes, compilação nativa, verificação do executável e teste do instalador Windows. A verificação empacotada usa dados temporários, exporta os dez POPs e confere um cálculo e uma análise observada. Não equivale a teste manual de todos os fluxos ou bancada. Instalador sem assinatura digital e Mac com assinatura ad hoc, sem notarização.

A falha de leitura cp1252 foi corrigida com UTF-8 explícito tanto no catálogo inicial quanto no formulário de formulação. Fontes, dados anteriores e histórico permanecem preservados.

## Histórico das distribuições locais

# Distribuição — Windows como prioridade

Nome: **Planejador de Experimentos**. O bundle `.app` inclui Python, PyQt6, bibliotecas científicas, catálogo e ícone; não exige abrir terminal nem ativar `.venv` para usar.

## Entrega principal: Windows

O alvo principal é um aplicativo **desktop nativo para Windows**, com executável `.exe`, interface PyQt6 e bibliotecas empacotadas para uso sem instalação manual de Python. macOS é suporte secundário. Nenhuma decisão de interface ou dependência deve tornar o Windows uma adaptação posterior.

A compilação e a validação do `.exe` precisam ocorrer em ambiente Windows, verificando inicialização, catálogo, planejamento, estatística, gráfico, exportação e instância única. O `.app` abaixo não comprova esses testes nem é um executável Windows. **Estado: build e validação Windows pendentes.** A receita `packaging/Planejador.spec` é específica do macOS e não deve ser usada como receita Windows.

## Suporte secundário: gerar macOS a partir do código

No macOS, na raiz do repositório:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[ui,bundle]"
.venv/bin/pyinstaller --noconfirm --distpath /private/tmp/planejador-build packaging/Planejador.spec
```

A saída é `/private/tmp/planejador-build/Planejador de Experimentos.app`. A construção temporária evita metadados que provedores de arquivos do Desktop podem anexar aos bundles durante a assinatura local. Copiar o bundle inteiro para o Desktop; não mover apenas o binário interno. Esta compilação é para o macOS/arquitetura da máquina de build, não gera um executável Windows.

O ícone fonte está em `frontend/assets/app.png`; a versão macOS em `app.icns`. A receita inclui esses recursos e `frontend/protocolos.json`. Recompilar após mudanças no código: o app empacotado não se atualiza sozinho. Fechar a instância anterior antes de testar uma nova compilação; QLockFile impede duplicatas.

Não versionar `build/`, `dist/` ou `.venv/`. O histórico atual dos preparos é persistente em SQLite; empacotar não transforma os cálculos em protocolos científicos validados. O bundle local usa assinatura ad hoc do empacotador, sem notarização de distribuição por conta Apple.

## Compilação Windows preparada em 08/11/2026

No PowerShell do Windows, a partir do checkout: `./packaging/build-windows.ps1`. A receita cria/usa `.venv`, instala os extras ui/bundle e gera `dist/Planejador-Windows.zip`, com executável e `Registros de Experimentos/LEIA-ME.txt`. Extrair o ZIP antes de abrir o executável. A compilação deve ocorrer no próprio Windows; a receita não foi executada neste Mac. Lucas optou por preparar e testar posteriormente, pois não tinha Windows disponível.

O arquivo `PlanejadorWindows.spec` usa a mesma entrada Qt e catálogo da aplicação macOS, com recursos necessários ao DOCX. A pasta do histórico SQLite fica nos dados do usuário; os arquivos arquivados usam a pasta portátil quando gravável e mostram o caminho na tela inicial.


## Pacote Mac PREP-001 a PREP-003

`output/distribuicao/Planejador-Mac-PREP-001-a-003.zip`: cálculo percentual, molar e de estoque, perguntas condicionais, edição com gráfico ao vivo, histórico de dez, três POPs ilustrados e pasta de registros. Build e assinatura ad hoc verificados em diretório temporário; catálogo e imagens incluídos, CRC do ZIP aprovado. A sessão do Desktop que estava aberta foi preservada; fechar antes de substituir pelo aplicativo extraído. A inspeção do fluxo foi em Qt de desenvolvimento, sem teste completo de cliques no novo bundle. Windows permanece com receita para compilação posterior no PC, conforme decisão de Lucas.


Pacote PREP-001 a PREP-004: `output/distribuicao/Planejador-Mac-PREP-001-a-004.zip`, com aplicativo, quatro POPs e pasta Registros de Experimentos. Assinatura local, catálogo empacotado, imagens e CRC do ZIP conferidos. A sessão Desktop em uso não foi substituída. A inspeção do fluxo foi em Qt de desenvolvimento; não foram repetidos cliques no bundle. Windows continua com compilação/teste adiado conforme decisão de Lucas.


Pacote Mac PREP-001 a PREP-005: `output/distribuicao/Planejador-Mac-PREP-001-a-005.zip`, com aplicativo, cinco POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Ajuste final de margens do gráfico seguido por 19 testes de interface aprovados. Sessão Desktop preservada; fluxo conferido em Qt de desenvolvimento, sem novos cliques no pacote. Windows permanece preparado para execução posterior, conforme escolha de Lucas.


Pacote Mac PREP-001 a PREP-006: `output/distribuicao/Planejador-Mac-PREP-001-a-006.zip`, com aplicativo, seis POPs e pasta Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows continua com compilação/teste preparado para execução posterior no PC, conforme escolha de Lucas.


Pacote Mac PREP-001 a PREP-007: `output/distribuicao/Planejador-Mac-PREP-001-a-007.zip`, com aplicativo, sete POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, três imagens de equipamentos e CRC conferidos. Após o ajuste final do texto explicativo, 153 testes de cálculo/interface passaram novamente. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows permanece preparado para compilação/teste posterior no PC, conforme escolha de Lucas.


Pacote Mac PREP-001 a PREP-008: `output/distribuicao/Planejador-Mac-PREP-001-a-008.zip`, com aplicativo, oito POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Módulo frontend.formulacao confirmado no arquivo PYZ; teste do fluxo de formulação passou novamente após ajuste final da altura das linhas. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows permanece preparado para compilação/teste posterior no PC, conforme escolha de Lucas.


Pacote Mac PREP-001 a PREP-009: `output/distribuicao/Planejador-Mac-PREP-001-a-009.zip`, com aplicativo, nove POPs e Registros de Experimentos. Assinatura local, catálogo empacotado idêntico ao código, imagens e CRC conferidos. Módulo frontend.meio_comercial confirmado no PYZ. Sessão Desktop preservada; fluxo inspecionado em Qt de desenvolvimento, sem novos cliques no bundle. Windows permanece preparado para compilação/teste posterior no PC, conforme escolha de Lucas.


Regularização de fontes concluída: pacote `output/distribuicao/Planejador-Mac-PREP-001-a-009-fontes-regularizadas.zip` (82.720.131 bytes), com catálogo atualizado, nove POPs e pasta de registros. Assinatura ad hoc, igualdade do catálogo empacotado, CRC e presença dos nove POPs conferidos. Sessão Desktop e dados existentes preservados; sem repetir cliques no bundle ou testes Windows. Fonte regularizada não equivale à inclusão formal ou comprovação da edição mais recente.


Pacote Mac PREP-001 a PREP-010: `output/distribuicao/Planejador-Mac-PREP-001-a-010.zip` (82.892.217 bytes), aplicativo, dez POPs e pasta de registros. Assinatura ad hoc, igualdade do catálogo empacotado, dez fichas com cálculo/fontes/imagem, recursos de equipamento e CRC do ZIP aprovados; sem banco de dados de usuário no pacote. Sessão Desktop preservada. Fluxo Qt de desenvolvimento inspecionado; sem repetir cliques no bundle ou testar Windows. Próxima entrega: integrar medições/estatística e exportações ao fluxo real dos dez protocolos, mantendo planejado e observado distintos.

Preparação Windows ajustada para gerar também os dez POPs ilustrados dentro do ZIP, reutilizando o exportador da aplicação; erros interrompem o empacotamento. Trecho Python teve sintaxe conferida. PowerShell, executável e documentos gerados no Windows continuam sem execução/teste nesse sistema.


Pacote com medições integradas: `output/distribuicao/Planejador-Mac-PREP-001-a-010-integrado.zip` (82.894.936 bytes). Aplicativo, dez POPs e pasta de registros; assinatura ad hoc, catálogo idêntico ao código, presença da nova integração no PYZ e CRC verificados. Nenhum banco de usuário incluído. Sessão Desktop preservada; cliques no novo bundle e compilação/teste Windows ainda não realizados.


Pacote Mac r2: `output/distribuicao/Planejador-Mac-PREP-001-a-010-integrado-r2.zip` (82.897.277 bytes). Inclui a recuperação de gravação, dez POPs e pasta de registros. Assinatura, catálogo idêntico ao código, funções de recuperação no PYZ e CRC aprovados. A cópia Desktop em uso foi preservada; sem novos cliques no bundle ou compilação/teste Windows. Pendências gerais em [conferência da entrega](../modulos/CONFERENCIA_ENTREGA.md).


## Windows disponível — 2026-11-08T18:45:43.747607-03:00

Lucas está no Mac com o PC Windows ao lado. As ferramentas deste chat continuam no Mac; nenhuma compilação Windows foi declarada. Pacote fonte isolado em `~/Desktop/Planejador-Fonte-Windows.zip`, sem `.venv`, dados de experimentos ou executável Mac. Extrair a pasta no Windows e abrir `COMPILAR-WINDOWS.cmd`; exige Python 3.11+ com `py` e internet. O launcher chama a receita existente e mantém a janela aberta para mostrar erros. A política PowerShell é definida apenas para esse processo, sem mudança permanente. Resultado previsto: `dist/Planejador-Windows.zip`, com exe, POPs e Registros de Experimentos. Ainda depende da execução e conferência reais no Windows.

Verificação de distribuição em 2026-11-08T19:28:57-03:00: instalação/desinstalação Windows e pacote Mac aprovados no [CI 42529979732](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions/runs/42529979732). Detalhes e limites em `../modulos/CONFERENCIA_ENTREGA.md`.

## Candidata 0.2.9 — 09/11/2026

Implementação de coleta/Excel/relatório integrada aprovada no [CI 42567226528](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions/runs/42567226528), incluindo executáveis Mac/Windows, instalador por usuário e preservação do arquivo de teste na desinstalação. O smoke agora também gera e confere um modelo de coleta Excel e exporta resultados em três formatos. Arquivos do pesquisador não integram os pacotes.

A instalação deste Mac permanece 0.2.8 até desbloqueio, fechamento seguro e conferência da nova janela. Preparar os artefatos não significa que a cópia instalada já foi atualizada. A conclusão geral permanece em [critérios de conclusão](../modulos/CONCLUSAO_APLICATIVO.md).
