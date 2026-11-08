# PREP-006 — Fator de diluição e concentração final

## Procedência regularizada em 08/11/2026

Cópia integral obtida efetivamente no Arca e idêntica byte a byte à fonte anterior. Consulta 2026-11-08T10:43:13.707165-03:00 (America/Maceio). Volume 1: https://www.arca.fiocruz.br/handle/icict/8658. Datas de obtenção, hashes e comparação em [regularização das fontes](../referencias/REGULARIZACAO_FONTES.md). Regras e páginas não mudaram; não equivale a inclusão formal na revisão nem confirmação de edição mais recente.

## Implementação de 08/11/2026

Perguntas próprias: concentração inicial C1 e unidade por volume, alíquota V1 em mL e volume final V2 em mL. Valores essenciais começam sem resposta; identificação de estoque/diluente é opcional. Não pede concentração final, pureza ou massa molar como entrada.

Fonte: Fiocruz v. 1, 2009, p. 232, relação C1 V1 = C2 V2. Rearranjos explícitos F=V2/V1 e C2=C1×(V1/V2). P. 230–231 sustenta técnica geral de transferência e aferição. Fonte integral, hash, consulta com data/horário/fuso e imagem complementar em [REGISTRO.md](../../REGISTRO.md) e FIOCRUZ-2009-vol1-PREP-006.json. Livro candidato ao recorte, sem inclusão formal ou comprovação de edição mais recente.

V1 não pode superar V2; igualdade significa fator 1. Entradas positivas/finitas e tipos numéricos validados; resultados fora da faixa numérica rejeitados. A mesma unidade de concentração por volume é mantida. % m/m excluído; % v/v limitado a 100%. Diferença V2−V1 é nominal; completar com diluente q.s.p. ao volume final, sem pressupor volumes aditivos. Cálculo não verifica solubilidade, estabilidade ou tolerância instrumental.

Plano mostra alíquota, fator e concentração calculada. Resultados permite editar C1, V1 e V2; curva de concentração por volume final mantém estoque/alíquota fixos, com ponto do preparo informado. Sem observações simuladas ou validação em bancada. Histórico preserva o mesmo registro nas edições válidas; exportação JSON inclui parâmetros/resultados e fontes.

219 testes passaram na suíte completa, cobrindo casos independentes, fator 1, entradas inválidas/incompatíveis, prevenção de estouro intermediário, recálculo/gráfico, histórico e exportações. Ruff e mypy dos módulos alterados com imports omitidos aprovados, sem tipagem completa das dependências. DOCX ilustrado renderizado e conferido em duas páginas; capturas Qt inspecionadas, página de 880 px sem rolagem horizontal e texto explicativo sem corte.

Pacote Mac PREP-001-a-006 gerado com seis POPs e pasta de registros; assinatura, catálogo e integridade verificados. Windows ainda não executado.

## Registro anterior preservado

# PREP-006 — Cálculo de fator de diluição e concentração final

**Estado:** candidato P1 selecionado para a lista da interface; não é ficha operacional validada nem cálculo específico implementado.

## Origem e datas

- Consulta do catálogo local e inclusão: 2026-10-30T04:56:36-03:00 (`America/Maceio`).
- Fonte consultada: F03, Catálogo de Priorização, v1.0, agosto/2026, tabela de preparações, linha PREP-006.
- Documento: https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit
- Evidência de importação: `frontend/protocolos.json`, registro PREP-006, extraído de `contexto/catalogo_protocolos.json` do acervo analisado anteriormente.
- Fontes apontadas pelo catálogo: B4 — Microbiologia Aplicada; B5 — Microbiology Society.
- Data/hora de consulta às fontes primárias: **não registrada**. As referências apontadas não foram consultadas nesta inclusão.

## Seleção

Rotina básica de preparo/cálculo, com potencial de reutilização no núcleo comum e menor dependência de interpretação de ensaios microbiológicos. A inclusão na lista é uma escolha de desenvolvimento de Lucas, não inclusão automática no corpus da revisão.

## Pendências para cálculo operacional

Conferir fonte integral, edição, páginas, finalidade, procedimento, materiais/reagentes, unidades, entradas, fórmulas, controles e limitações pertinentes. Registrar a origem de cada trecho antes da implementação. Priorizar as fontes da metodologia da revisão, começando por Anvisa quando aplicável; as demais referências são complementares até avaliação de elegibilidade.

Nenhuma instrução de bancada ou quantidade foi criada por suposição. Ver a regra de proveniência em `README.md` desta pasta.
