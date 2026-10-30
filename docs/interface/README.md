# Interface — fluxo único

Aplicação desktop PyQt6 em `~/Desktop/INICIACAO CIENTIFICA`, baseada nos requisitos e nos services existentes. Abra na raiz com `.venv/bin/python -m frontend.app` (instalação: `pip install -e ".[ui]"`). Apenas uma instância é permitida.

## Jornada

1. **Início:** iniciar um novo planejamento.
2. **Protocolo:** clicar no próprio campo para abrir sugestões e digitar nome/código, com ou sem acentos. Selecionar e confirmar para avançar.
3. **Parâmetros:** informar os dados e gerar o plano. Plano fica bloqueado até uma geração válida.
a4. **Plano:** conferir cálculo, insumos e organização; continuar para registrar medições.
5. **Resultados:** preencher grupos e valores observados na tabela, informar a grandeza/unidade, ver resumo e gráfico. Nome do experimento, protocolo e organização planejada acompanham esta etapa.

Na tabela de resultados, cada linha representa um grupo; separar seus valores com ponto e vírgula (`1,2; 1,4; 1,3`). Nenhuma medição é inferida a partir do planejamento. Média e desvio padrão recebem explicação simples. Comparação t/ANOVA é opcional nas opções avançadas, sem verificar automaticamente pressupostos ou independência das repetições.

## Coerência e salvamento

Mudar o protocolo ou iniciar outro planejamento limpa parâmetros, plano e resultados. Editar parâmetros invalida o plano e suas observações/análises; editar só medições mantém o planejamento e limpa apenas análise/gráfico. É possível voltar ao mesmo plano.

Salvar tudo em JSON reúne parâmetros, plano, medições, unidade e análise do mesmo experimento. O gráfico pode ser salvo em PNG. Os dados da interface ficam em memória; não há autosave ou reimportação nesta prévia. Exporte antes de iniciar outro fluxo.

## Catálogo e limites

Há dez candidatos P1 (PREP-001 a PREP-010) com fichas de proveniência em `docs/protocolos/`, além dos dois exemplos do backend. Candidatos ainda sem regras científicas verificadas não geram planos operacionais fictícios. As fontes/versões científicas dos exemplos continuam pendentes. SQLite em memória isola a prévia do banco real.

A UI chama services diretamente, sem HTTP e sem duplicar fórmulas. Matplotlib apresenta os pontos observados por grupo. Persistência das medições no banco e outros gráficos são próximos ciclos.

## Verificação

50 testes direcionados, inspeção Qt em 1180 e 880 px e conferência da janela nativa. Capturas em `capturas/`; evidências e limitações em [AUDIT.md](AUDIT.md). Acessibilidade usa widgets/foco/labels nativos e rolagem; não foi feita auditoria completa com leitores de tela nem teste de usabilidade com participantes.
