"""Camada de API opcional (FastAPI).

Só é necessária se você quiser expor o backend por HTTP (ex.: para um frontend
web ou integração externa). Requer o extra ``api``:

    pip install -e ".[api]"
    uvicorn planejador.api.app:app --reload

Para o frontend desktop em PyQt6, esta camada NÃO é necessária — a UI pode
chamar os ``services`` diretamente.
"""
