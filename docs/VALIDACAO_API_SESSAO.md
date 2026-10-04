# API real, isolamento entre contas e renovação — 03/10/2026

## Evidência recebida

Usuário executou VALIDAR_API_SESSAO_APOLO.py no terminal normal, dentro do clone
original em 2486215. Senhas e chave digitadas ocultamente apenas no computador;
nenhuma credencial enviada ao agente. Saída recebida: **isolamento HTTP com dois
JWTs e renovação real APROVADOS**, com encerramento local das duas sessões.
É evidência de execução do usuário, não uma execução feita pelo agente no sandbox.
Não somar esses controles aos 696 testes da CI; são validação externa adicional.

## Permitido e negado, de verdade

| Verificação | Conta 1 | Conta 2 |
| --- | --- | --- |
| Identidade confirmada pelo Auth e papel OPERADOR | Aprovado | Aprovado |
| Refresh HTTP real e identidade revalidada | Aprovado | Aprovado |
| Lista de projetos sem filtro de dono só contém próprios | Aprovado | Aprovado |
| Variáveis, histórico e snapshots próprios acessíveis | Aprovado | Aprovado |
| Diagnóstico próprio recusado ao OPERADOR | HTTP 403 | HTTP 403 |
| projects alheios invisíveis | Lista vazia | Lista vazia |
| project_values alheios invisíveis | Lista vazia | Lista vazia |
| executions alheias invisíveis | Lista vazia | Lista vazia |
| execution_values alheios invisíveis | Lista vazia | Lista vazia |
| profiles alheios invisíveis | Lista vazia | Lista vazia |
| RPC para projeto alheio recusada antes da gravação | HTTP 403 | HTTP 403 |
| Logout local da sessão criada pelo verificador | Confirmado | Confirmado |

Projeto E2E A conservou seis execuções. A segunda conta tinha projeto próprio
com histórico, portanto as consultas cruzadas miraram recursos existentes,
não IDs fictícios sem linhas. Leitura própria positiva ajuda a distinguir RLS
real de tabela vazia/credencial quebrada. HTTP 401, 400 e erro de rede não seriam
aceitos como negação RPC. O dono não é apenas um filtro aplicado na interface.

O probe da RPC usa cálculo inexistente e snapshots vazios: se o guard de dono
falhasse, a validação do cálculo abortaria antes de qualquer INSERT. O script
exigiu 403, não aceitou 400 como sucesso. Não cria cálculo/projeto, não configura
valores, não promove perfil, não faz DELETE/PATCH nem instala migrations.

## Limites honestos

A renovação usou endpoint Auth real, acionada ao expirar SOMENTE o relógio da
sessão do verificador. Não aguardamos expiração natural do JWT no servidor nem
alteramos TTL/configuração. Os testes automatizados cobrem sessão expirada,
refresh revogado/rede/perfil inválido, mas isso não é expiração natural real.
Logout local encerrou só sessões de teste; JWT já emitido pode continuar válido
até vencer. Não alegar revogação imediata de access token.

A matriz HTTP cruzada desta execução usa dois OPERADORES. ADMIN/DESENVOLVEDOR
foram aprovados antes pela UI própria e SQL real com claims controlados/rollback.
Não afirmar que houve JWT administrativo cruzado ou PATCH direto de promoção
de perfil nesta execução. Grants contra promoção direta foram verificados na CI
PostgreSQL e auditoria SQL do Supabase. É um piloto funcional, não auditoria externa.

## Git, integração e próximos passos

Sem mudança de runtime, fórmula, fixture, dependência ou SQL. Registro na
feature/production-validation, criada do develop isolado em 2486215.
Criado este documento; alterados manual/changelog, README e registro de produção.
Conferência git diff --check; mesmo runtime da CI 37165709281: 696/3/0,
e pytest padrão do usuário 691/8/0. Não houve nova suíte estrutural nesta edição
documental. Hash do novo commit no relatório entregue.

Consolidação ainda necessária no clone original/GitHub: importar documentos,
testar, integrar por fast-forward em develop e atualizar feature/render-deploy,
publicar sem force e conferir a CI do novo tip. Main continua a4cd61a.
O roteiro entregue cria backups, exige árvore limpa e ancestry compatível;
recusa DSN PostgreSQL de testes definido para não executar SQL em banco real.
Não faz deploy, alteração Supabase ou contratação. Runtime Live permanece 2486215.

Após consolidar o ramo configurado no Render, Deploy latest commit deixa de
apontar para o código antigo f669ce2; auto-deploy continua off. Até confirmar
essa publicação, preferir SHA específico validado. Backup/carga/limites Free,
idempotência, recuperação de senha e demais extensões ficam documentados.
