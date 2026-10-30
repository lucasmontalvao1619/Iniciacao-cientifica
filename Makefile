.PHONY: help dev db test lint format type-check api clean

# O pacote vive em backend/. Apontar o PYTHONPATH para lá torna os alvos
# independentes do install editável: em macOS, o sistema pode marcar os
# arquivos .pth de site-packages com a flag UF_HIDDEN, e o `site` do Python
# >= 3.11 ignora .pth ocultos — o que faz `import planejador` falhar mesmo
# depois de `make dev`. Ver a mesma nota em pyproject.toml.
export PYTHONPATH := backend

help:
	@echo "Alvos: dev db test lint format type-check api clean"

dev:
	pip install -e ".[dev]"

db:
	python -m planejador.bootstrap

test:
	pytest

lint:
	ruff check backend tests

format:
	ruff format backend tests
	ruff check --fix backend tests

type-check:
	mypy backend

api:
	uvicorn planejador.api.app:app --reload

# Remove só o que é regenerável. Não toca em .venv (o bytecode de lá é
# recriado a cada import, e varrê-lo só deixa a próxima execução mais lenta)
# nem em *.egg-info, que sustenta o install editável.
clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +
