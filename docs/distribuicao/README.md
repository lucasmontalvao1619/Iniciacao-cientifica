# Aplicativo macOS

Nome: **Planejador de Experimentos**. O bundle `.app` inclui Python, PyQt6, bibliotecas científicas, catálogo e ícone; não exige abrir terminal nem ativar `.venv` para usar.

## Gerar a partir do código

No macOS, na raiz do repositório:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[ui,bundle]"
.venv/bin/pyinstaller --noconfirm --distpath /private/tmp/planejador-build packaging/Planejador.spec
```

A saída é `/private/tmp/planejador-build/Planejador de Experimentos.app`. A construção temporária evita metadados que provedores de arquivos do Desktop podem anexar aos bundles durante a assinatura local. Copiar o bundle inteiro para o Desktop; não mover apenas o binário interno. Esta compilação é para o macOS/arquitetura da máquina de build, não gera um executável Windows.

O ícone fonte está em `frontend/assets/app.png`; a versão macOS em `app.icns`. A receita inclui esses recursos e `frontend/protocolos.json`. Recompilar após mudanças no código: o app empacotado não se atualiza sozinho. Fechar a instância anterior antes de testar uma nova compilação; QLockFile impede duplicatas.

Não versionar `build/`, `dist/` ou `.venv/`. Os dados desta prévia continuam em memória até exportação; empacotar não transforma os candidatos em protocolos científicos validados. O bundle local usa assinatura ad hoc do empacotador, sem notarização de distribuição por conta Apple.
