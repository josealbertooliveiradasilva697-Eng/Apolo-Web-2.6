# Papéis e isolamento no ambiente real — 03/10/2026

Continuação da etapa 10, código remoto f669ce2. O usuário confirmou a segunda
conta e autorizou testar temporariamente ADMIN e DESENVOLVEDOR na conta indicada,
restaurando OPERADOR. Os logins foram feitos pelo usuário: nenhuma senha recebida,
token extraído ou chave administrativa introduzida na aplicação.

## Contas e escopos

`supabase/verificacoes/20261003_perfis_precheck.sql` confirmou três profiles,
todos originalmente OPERADOR. Somente josealberto290@outlook.com foi promovido
durante o teste, com guarda por UUID, email, papel anterior e exatamente uma linha.

Na segunda conta conectada, o seletor apresentou apenas Alberto2. A/B e 123 da
primeira conta não apareceram; histórico e banco de variáveis abriram normalmente.
Na primeira conta apareceram apenas 123 e os projetos E2E A/B, não Alberto2.
Todas as configurações de teste foram limitadas ao projeto E2E A.

## Banco real

`20261003_papeis_isolamento.sql` exige donos distintos e seis execuções auditadas
em A. Em uma transação, claims SQL controlados e `authenticated` verificaram:

- ADMIN: consulta/configuração própria permitida; diagnóstico próprio, configuração
  e gravação alheias, falsificação do dono e UPDATE de profiles negados.
- DESENVOLVEDOR: configuração/diagnóstico próprio permitido (seis execuções,
  23 variáveis); diagnóstico, configuração e gravação alheios negados.
- Segunda conta OPERADOR: projeto próprio visível; dados de A invisíveis e sua
  gravação negada.
- Isolamento de projects, project_values, executions e execution_values.

Todas as assertions passaram: resultado `true / true / operador`.
ROLLBACK desfez configurações e papéis dessa transação. Isso exercita PostgreSQL,
RLS e RPC reais, NÃO tentativas HTTP negativas com JWTs distintos. O caminho HTTP
normal do aplicativo foi exercitado por cada conta; o teste hostil direto falta.

## Interface e retorno

A sequência temporária foi OPERADOR -> ADMIN -> DESENVOLVEDOR -> OPERADOR.
ADMIN exibiu Administração, sem Diagnósticos. Em A, status_projeto foi salvo como
`Validacao ADMIN 2026-10-03`; uma consulta independente confirmou o texto e seis
execuções preservadas. DESENVOLVEDOR exibiu ambas as páginas; o diagnóstico
pela interface retornou backend supabase, seis execuções e 23 variáveis.
Voltando a OPERADOR, o rerun revalidou o perfil e retirou ambas as páginas.

A primeira tentativa de restaurar o texto indicou sucesso, mas o banco ainda
continha o anterior. Saindo/voltando à página, o texto foi restaurado pela UI.
Consulta final `20261003_estado_ui.sql`: OPERADOR / Conectado com sucesso / 6.
Nenhum privilégio temporário ou configuração de teste ficou ativo.

Essa inconsistência motivou quatro regressões: dois papéis, entrada textual e
numérica, dois envios consecutivos, conferidos no repository. Antes da correção,
os quatro falharam no SEGUNDO envio: 4 failed, 691 deselected. Defeito reproduzido
sem internet; problema de estado do formulário, não de cálculo, RLS ou banco.
A correção será isolada em feature própria antes de nova publicação.

## Evidências e pendências

Sem nova migration/schema, fórmula, fixture ou dado legado alterado.
CI de referência: 688 passed, 3 skipped, 0 failed para f669ce2, não para a correção.
Evidências em outputs: E2E_SEGUNDA_CONTA_APOLO.jpg,
E2E_RLS_DUAS_CONTAS_APOLO.jpg, E2E_ADMIN_APOLO.jpg,
E2E_DESENVOLVEDOR_APOLO.jpg e E2E_RETORNO_OPERADOR_APOLO.jpg.

Pendentes: corrigir/publicar/revalidar o formulário, API negativa entre contas,
expiração/refresh real, restart e novo deploy com histórico persistido.
