# Protocolos

Protocolos laboratoriais suportados pelo sistema.

Um protocolo é **dado**, não código: vive na tabela `protocolos` com seus
vínculos de reagente e material. Cadastrar um novo não exige alterar módulos —
ver [decisões](../decisoes/README.md).

> **Nenhum protocolo deve ser implementado antes de estar documentado aqui.**

## O que cada protocolo deve registrar

- nome do protocolo;
- área experimental;
- objetivo;
- variáveis de entrada;
- materiais necessários;
- reagentes necessários;
- volumes;
- concentrações;
- diluições;
- controles;
- repetições;
- etapas operacionais;
- limitações;
- referências.

## Tipos de protocolo

O campo `tipo` determina quais cálculos o sistema aplica ao gerar o plano:

| `tipo` | Cálculos aplicados |
|---|---|
| `preparo_solucao` | Escalonamento de reagentes e materiais |
| `diluicao` | Escalonamento; diluição simples ou seriada |
| `microplaca` | Escalonamento **e** organização de poços e placas |

Um `tipo` não reconhecido ainda gera plano com o escalonamento — apenas não
recebe os cálculos específicos.

## Protocolos cadastrados

Dois protocolos de exemplo são semeados automaticamente na primeira execução
(`backend/planejador/database/seed.py`), para que o sistema seja executável
imediatamente:

| Nome | Tipo |
|---|---|
| Preparo de solução salina 0,9% | `preparo_solucao` |
| Ensaio de crescimento em microplaca | `microplaca` |

São exemplos de demonstração. Protocolos reais do projeto devem ser documentados
neste diretório — um arquivo por protocolo — antes de serem cadastrados.

Ver [planejamento experimental](../modulos/planejamento-experimental.md) para
como o plano é gerado a partir de um protocolo.
