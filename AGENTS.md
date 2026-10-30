# AGENTS.md

## Projeto

Desenvolvimento de um aplicativo para planejamento automático de experimentos laboratoriais e análise estatística.

## Objetivo geral

Auxiliar pesquisadores e estudantes no planejamento de experimentos laboratoriais, gerando apoio operacional a partir de protocolos, variáveis experimentais e dados fornecidos pelo usuário.

## Escopo inicial

- Microbiologia.
- Preparo de soluções.
- Diluições seriadas.
- Ensaios em microplacas.
- Organização de controles.
- Repetições experimentais.
- Análise estatística básica e inferencial.

## Escopo futuro

- Química.
- Fenólicos.
- Flavonoides.
- Antioxidantes.
- Ensaios biológicos.
- Novos protocolos experimentais.

## Tecnologias

- Python (>=3.11).
- PyQt6 (interface — ainda não implementada).
- SQLite via SQLAlchemy (banco atual; Postgres/MySQL plugáveis pela variável
  `APP_DATABASE_URL`). Ver `docs/decisoes/README.md`.
- NumPy, Pandas, SciPy, Matplotlib (cálculos e estatística).

## Arquitetura (estado atual)

O backend já foi implementado. Estrutura real do código:

- `backend/planejador/core/`: cálculos e estatística puros (implementado).
- `backend/planejador/database/`: acesso a dados via SQLAlchemy (implementado).
- `backend/planejador/services/`: orquestração core + database (implementado).
- `backend/planejador/api/`: API HTTP opcional em FastAPI (implementado).
- `backend/planejador/bootstrap.py`: inicialização do banco.
- `frontend/`: interface PyQt6 — ainda não implementada.
- `database/`: `schema.sql` (referência do modelo) e `seed.sql`.
- `tests/`: testes (pytest) do backend — implementado.
- `docs/`: fonte principal de contexto.

Dependência entre camadas apenas "para baixo": `ui/api → services → core / database`.
Ver `backend/README.md` para como executar e `docs/arquitetura/` para detalhes.

## Fluxo obrigatório

Antes de implementar qualquer funcionalidade:

1. Ler `docs/README.md` (índice da documentação)
2. Ler `docs/visao-geral.md`
3. Ler `docs/requisitos/`
4. Ler `docs/decisoes/README.md`
5. Consultar a documentação relevante em `docs/`
6. Consultar a pasta `Análise de dados IC` quando precisar de contexto adicional, protocolos, referências ou conhecimento do domínio.

A pasta `docs/` é organizada por tema: cada subpasta tem um `README.md` que é a
porta de entrada daquele tema. Não criar arquivos soltos na raiz de `docs/` que
dupliquem o conteúdo de uma subpasta.

Regras:

- A pasta `docs/` é a fonte oficial de documentação do projeto.
- A pasta `Análise de dados IC` é a memória de longo prazo do projeto. Guarda
  apenas as notas em `.md`; a configuração do Obsidian (`.obsidian/`) e os
  caches de plugin (`.smart-env/`) ficam fora do versionamento e são recriados
  pelo próprio aplicativo.
- Não contradizer decisões registradas em `docs/decisoes/README.md`.
- Atualizar documentação sempre que uma decisão arquitetural importante for tomada.
- Antes de grandes implementações, revisar a documentação existente.

## Regras para futuras IAs

- Antes de implementar qualquer coisa, leia `docs/`.
- Use `docs/` como fonte principal de contexto permanente.
- Mantenha consistência com a arquitetura modular.
- Documente decisões em `docs/decisoes/README.md`.
- Não versionar `.obsidian/` nem `.smart-env/` — são configuração e cache do
  Obsidian, não conteúdo do projeto.
- Não apagar notas antigas.
- Não remover conhecimento sem autorização explícita.
- Não implementar código sem pedido explícito.
- Não criar funcionalidades, telas, APIs, banco, cálculos ou estatística sem pedido explícito.
