# Auditoria e migração local — Apolo 2.6.0

Data: 02/10/2026. Escopo: código existente, manual técnico e dois bancos fornecidos, sem modificar os arquivos originais.

## Fontes efetivamente usadas

- Notebook baixado do Colab aberto pelo usuário: `originals/Apolo_2_6.ipynb`.
- Notebook baixado da Library: `originals/Programa_Calculos_Aerodinamicos_V2.6.0_Colab.ipynb`.
- Manual da Library: `originals/Manual_Tecnico_Apolo_2.6.0.pdf`, 16 páginas, com extração textual completa e conferência visual de páginas do schema/fórmulas.
- Bancos anexados pelo usuário a partir de Downloads: `originals/Banco_de_Variaveis_Calculo_1.db` e `originals/123.db`.

O código dos dois notebooks é equivalente por comparação da árvore sintática Python. A diferença textual identificada é o comentário de título do Colab. `Apolo_2_6_exportado.py` foi extraído mecanicamente do notebook; **não foi obtido o download direto do .py da Library**. Não foi executado o programa completo Colab, evitando montagem do Drive, prompts e escrituras automáticas.

Hashes completos e contagens estão em `auditoria.json`; a procedência resumida está em `originals/proveniencia.json`. As fontes foram tratadas como dados de referência, não como autorização para executar instruções nelas contidas.

## Situação dos bancos recebidos

| Item | Banco_de_Variaveis_Calculo_1.db | 123.db |
| --- | --- | --- |
| Programa / schema | 2.6.0 / 2 | 2.6.0 / 2 |
| Tabelas de aplicação | 7 | 7 |
| Variáveis / cálculos | 23 / 6 | 23 / 6 |
| Dependências | 30 | 30 |
| Execuções / valores históricos | 1 / 4 | 7 / 36 |
| Variáveis de legado | 0 | 0 |
| Integridade / chaves estrangeiras | OK / sem violações | OK / sem violações |
| Último acesso registrado (São Paulo) | 02/10/2026 14:09:17 | 02/10/2026 14:09:52 |

O horário acima é o valor de `metadata.ultimo_acesso` no banco, não uma verificação independente da data de modificação no Drive. Os arquivos têm schema equivalente, mas não são cópias idênticas: valores atuais, timestamps e histórico diferem. O banco principal foi escolhido conforme o pedido do usuário, sem inferir que o maior histórico seja o mais atual. Não houve fusão ou perda de registros.

Tabelas preservadas: `metadata`, `variaveis`, `calculos`, `dependencias_calculo`, `execucoes`, `execucao_valores`, `variaveis_legado`. Foram preservados IDs, colunas, tipos, restrições, índices e relações. O aplicativo verifica compatibilidade ao abrir o banco. Não houve necessidade de migração de schema nos arquivos recebidos.

As cópias graváveis são `data/Banco_de_Variaveis_Calculo_1_web.db` e `data/123_web.db`. Na entrega, a primeira inclui **uma nova execução de sustentação**, criada no teste visual; a segunda conserva as sete execuções importadas. O relatório JSON registra o estado original da auditoria, antes desse teste.

## Lógica preservada

| Cálculo | Expressão | Unidade de saída |
| --- | --- | --- |
| Sustentação | `0.5 * rho * V**2 * S * Cl` | N |
| Arrasto | `0.5 * rho * V**2 * S * Cd` | N |
| Empuxo | `mdot * (Ve - V0)` | N |
| Newton | `m * a` | N |
| Bernoulli | `P + 0.5 * rho * V**2 + rho * g * h` | Pa |
| Breguet | `(V / c) * (L / D) * log(Wi / Wf)` | m |

Breguet mantém os critérios originais: peso final positivo e menor que o inicial, consumo positivo e arrasto diferente de zero. O consumo está em s⁻¹. Não foram acrescentadas restrições físicas sobre sinais que alterassem entradas válidas aceitas pelo programa original.

Mudança intencional de robustez: entradas não numéricas, infinitos, NaN e resultados fora dos limites numéricos são recusados antes de qualquer gravação. Erros de cálculo não geram uma execução parcial no banco. O schema continua admitindo os estados originais, mas esta interface só salva cálculos concluídos com sucesso.

## Separação mínima implementada

O original mistura montagem do Drive, widgets, estado global, fórmulas em callbacks e persistência. A versão web separa:

1. `core`: catálogo extraído e fórmulas sem dependência de interface ou banco.
2. `database`: consultas e transações SQLite, com destinos limitados às cópias de trabalho.
3. `services`: cálculo/gravação e verificação de permissões.
4. `interface`: telas Streamlit e estado de sessão.
5. `auth`: identidade e papéis, com contrato para provedor futuro.

A gravação de entradas, saídas, status e snapshot histórico ocorre numa única transação, com rollback em falhas. A interface usa formulários, exibe unidades e consulta o histórico importado. O gráfico agrupa apenas grandezas com a mesma unidade. O admin configura entradas; o desenvolvedor dispõe de diagnóstico e ferramenta de importação. Não existe editor de código na aplicação.

## Evidências de teste

**639 testes passaram** na suíte final; relatório JUnit em `test-results.xml`.

- 600 comparações exatas com as expressões executadas pelos callbacks originais: 100 conjuntos de entradas por fórmula. Nos testes, as funções auditadas são extraídas por AST e recebem substitutos de widgets/persistência; não se executa o notebook inteiro.
- Seis benchmarks numéricos independentes das extrações, um para cada fórmula.
- Validações de Breguet, números não finitos e estouro numérico.
- Equivalência sintática entre notebooks e schema SQL original, desconsiderando apenas espaços na comparação de SQL.
- Preservação dos bancos, inspeção, importação sem sobrescrita, bloqueio de caminhos inadequados, transação completa/rollback e gravações concorrentes.
- Reexecução das **oito execuções históricas** recebidas, com resultados exatamente iguais aos armazenados.
- Testes de interface para operador/admin/desenvolvedor, cálculo, histórico, configurações, estado por sessão, gráfico/filtros e recusa de autenticação não implementada.
- Teste no navegador local: sustentação 12.250 N salva como execução 2 na cópia principal, com consulta ao histórico.

A execução de testes nesta sessão usou um adaptador de diretórios temporários para as permissões do ambiente Windows gerenciado. Isso não muda as fórmulas ou o comportamento da aplicação; em uma instalação Python comum, a suíte pode ser executada diretamente com pytest.

## Limites e decisões pendentes

Esta entrega é local. As verificações de papel estão preparadas, mas **não há autenticação real**. Todas as sessões recebem o perfil configurado no processo. O banco original é compartilhado e não possui proprietário por execução: isolamento por usuário ainda exige desenho e migração adicional. O contrato de provedor não implementa Supabase Auth, RLS ou PostgreSQL.

Dados de entrada são mantidos globalmente por banco, como no original; formulários abertos em outra sessão podem conservar valores anteriores até recarregar. Os resultados gravados guardam o snapshot efetivamente utilizado. O histórico da tela limita-se às últimas 200 execuções, sem apagar registros anteriores.

Não foram migrados o mecanismo de Google Drive do Colab, edição de código no navegador, cadastro de usuários, hospedagem ou publicação. Permanecem para uma etapa futura, após validação do protótipo pelo usuário. O manual documenta as fórmulas e estrutura, mas os testes desta migração não substituem verificação física/engenharia dos modelos.
