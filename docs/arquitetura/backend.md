# Backend

Backend em Python organizado em camadas, com dependências apenas "para baixo"
(`ui/api → services → core / database`). Isso mantém o núcleo de cálculo
independente de banco e de interface, facilitando testes e manutenção.

## Camadas

- **core**: cálculos e estatística puros (sem banco, sem UI). Fácil de validar
  contra cálculos manuais (etapa 7.5 da metodologia).
  - `calculos.py`: diluição (C1V1=C2V2), diluição seriada, massa de soluto,
    escalonamento com excesso, planejamento de tubos e de microplaca.
  - `estatistica.py`: média, desvio, variância, erro padrão, teste t, ANOVA.
  - `tabelas.py`: organização dos dados em `DataFrame` (Pandas) e exportação CSV.
  - `exceptions.py`: erros de domínio (`EntradaInvalida`, `RegistroNaoEncontrado`).
- **database**: acesso a dados via SQLAlchemy. Todo o SQL fica isolado aqui.
  - `connection.py`: engine e sessão, agnósticos de motor.
  - `models.py`: tabelas (protocolos, reagentes, materiais, vínculos,
    experimentos, medições).
  - `repositories.py`: operações de leitura/escrita.
  - `seed.py`: dados de exemplo.
- **services**: orquestram core + database e são o ponto de entrada da UI/API.
  Cobrem o fluxo do aplicativo na ordem em que o usuário o percorre.
  - `planejamento_service.py`: gera o plano operacional (reagentes/materiais
    escalonados, preparo da solução, tubos, microplaca e resumo do procedimento).
  - `experimento_service.py`: seleção de protocolos e registro das medições
    obtidas na bancada, já devolvidas em tabelas.
  - `estatistica_service.py`: aplica as análises a dados em memória ou salvos e
    exporta os resultados em CSV.
- **api**: camada HTTP opcional (FastAPI), só necessária para frontend externo.
- **bootstrap.py**: cria as tabelas e semeia dados — "liga" o backend numa chamada.

## Como executar

Ver `backend/README.md` para instalação, inicialização do banco, uso dos
services, API opcional e troca de banco.

## Princípios de qualidade

Tipagem (mypy), lint/format (ruff), testes (pytest com SQLite em memória),
funções de cálculo puras e exceções de domínio tratadas na borda (UI/API).
