"""Backend do aplicativo de planejamento automatizado de experimentos laboratoriais.

Camadas:
    core       -> regras e cálculos puros (sem banco, sem UI).
    database   -> acesso a dados via SQLAlchemy (models, conexão, repositórios).
    services   -> orquestra core + database e expõe operações ao frontend/API.
    api        -> camada opcional (FastAPI) para expor os services via HTTP.
"""

__version__ = "0.1.0"
