# Frontend PyQt6

Fluxo navegável: início, protocolos, parâmetros, plano e resultados com estatística e gráfico. Usa o backend existente com dados demonstrativos em memória; não altera o banco real.

Na raiz do projeto:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[ui]"
.venv/bin/python -m frontend.app
```

O plano é gerado pelos services e pode ser exportado em JSON. As fontes científicas dos exemplos ainda não estão vinculadas. A tabela de medições e os gráficos pertencem ao mesmo planejamento; dados ficam em memória até exportação JSON/PNG.

Fluxo e auditoria: `docs/interface/`. No macOS deste ambiente, o provedor de arquivos marca plugins Qt como ocultos; a inicialização remove apenas esse flag dos plugins da instalação para que o Qt possa encontrá-los.
