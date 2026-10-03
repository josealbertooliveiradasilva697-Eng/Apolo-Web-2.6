# Validação real do operador — 03/10/2026

Código no Render: f669ce2. Aplicativo: https://apolo-web-z74k.onrender.com/.
Registro documental na feature/online-validation; nenhuma fórmula ou código de
execução alterado nesta etapa. Não há senhas, tokens ou e-mails neste registro.

## Sessão e projeto exclusivo

O usuário entrou na conta por conta própria. A tela confirmou papel OPERADOR,
permitindo Novo cálculo/Histórico/Banco de variáveis. Administração e Diagnósticos
não apareceram. Isso, sozinho, não prova a proteção no banco.

O projeto pré-existente do usuário (“123”) foi preservado. Criados pelo teste:

- Validacao E2E 2026-10-03 A: seis execuções válidas.
- Validacao E2E 2026-10-03 B: sem execuções, 23 defaults.

Ambos pertencem ao mesmo usuário; isso testa separação entre projetos, não
isolamento entre pessoas. Ao selecionar B o histórico ficou vazio; ao voltar
a A o histórico/detalhes reapareceram. Banco de variáveis também abriu.
Os projetos e snapshots de teste foram preservados, não apagados.

## Seis resultados independentes, do formulário até o banco

| Cálculo | Entradas na ordem do catálogo | Resultado esperado | Execução |
| --- | --- | --- | --- |
| CAL_SUST | 1.225, 50, 10, 0.8 | 12250 N | 4e6616bc-6413-45cd-aeb8-712d807e76ea |
| CAL_ARR | 1.225, 50, 10, 0.04 | 612.5 N | f8195ede-c5b3-4aa5-bb40-c2ab8a6102fd |
| CAL_EMP | 10, 500, 100 | 4000 N | 90543fb6-a9a3-48c4-808d-20effe3a724c |
| CAL_NEWTON | 1000, 2 | 2000 N | 3d9cb6df-0580-430b-86d2-83af273449cc |
| CAL_BER | 101325, 1.225, 50, 9.81, 100 | 104057.975 Pa | 6a4bbb9c-eed2-4b30-a27e-8660714139a2 |
| CAL_BREG | 100, 0.0002, 20000, 1000, 100000, 80000 | 2231435.5131420977 m | da86637e-7494-4435-ab69-bb1a24ad593b |

O aplicativo exibiu os seis resultados esperados (formato de dez algarismos
significativos). Bernoulli preservou gravidade 9.81 desabilitada no formulário.
Breguet carregou a sustentação/arrasto salvos anteriormente e permitiu usar
as entradas da referência independente.

Depois foi enviado Breguet com peso final igual ao inicial (100000). A interface
rejeitou com a mensagem de restrição, removeu o resultado anterior e não criou
uma sétima execução. Não alteramos as restrições matemáticas.

A consulta somente leitura supabase/verificacoes/20261003_e2e.sql foi copiada
do arquivo e conferida integralmente pelo conteúdo do editor antes de executar.
Resultado observado no Supabase:

- Profiles: **1**, todos OPERADOR (apenas uma conta encontrada neste momento).
- A: 23 variáveis, seis cálculos distintos, seis execuções SUCESSO do proprietário,
  30 valores de snapshot (24 entradas + seis saídas).
- As seis saídas: equivalente=true, comparação relativa 1e-12.
- B: 23 variáveis, zero execuções/snapshots.

A consulta JSON mostra Breguet como 2231435.5131421; essa apresentação não altera
a referência completa nem reduz os 600 testes de igualdade exata do core.
Este ensaio não substitui a suíte de 600 fixtures; ela já passou na CI.

## Autorização real no PostgreSQL do Supabase

supabase/verificacoes/20261003_operador.sql foi conferido integralmente e executado.
Ele valida projeto único/papel esperado, usa auth.uid() real do Supabase com
claims SQL de diagnóstico e SET LOCAL ROLE authenticated dentro de transação.
Não cria usuários, stubs, funções ou grants; não altera o papel em profiles.

O banco permitiu ler o próprio projeto e as seis execuções. Negou as chamadas
apolo_configure e apolo_diagnostics com SQLSTATE 42501; não havia grant UPDATE
para promover o próprio profile. ROLLBACK encerrou o teste; nenhuma configuração
foi persistida. O resultado final confirmou true para os bloqueios.

São verificações do banco real com contexto SQL controlado, NÃO tentativas
HTTP hostis no PostgREST com JWTs de duas pessoas. Não confundir essas evidências.
Se executar novamente após promover o perfil, o script deve recusar: exige OPERADOR.

## Logout e login negativo

Sair retornou ao formulário com campos vazios, removendo identidade, projetos,
navegação autenticada e resultados, sem aviso de falha de revogação.
Isso confirma o comportamento do logout; JWT já emitido pode valer até seu TTL.

Uma única tentativa com conta inexistente no domínio reservado example.invalid
foi recusada pelo Supabase e exibiu erro genérico seguro. Nenhuma senha real
foi usada/lida e não houve tentativa repetida contra a conta do usuário.
A aba foi deixada na tela de login para a próxima validação.

## Pendências e autorização necessária

Ainda falta criar/entrar na segunda conta e testar acesso cruzado via API,
ADMIN/DESENVOLVEDOR, expiração/refresh real, restart e novo deploy com histórico.
Foi solicitado ao usuário criar a segunda conta confirmada; nenhuma senha no chat.
Também foi solicitada confirmação para promover temporariamente somente a conta
já testada a ADMIN e depois DESENVOLVEDOR, restaurando OPERADOR. **Nenhuma promoção
foi executada nesta etapa.** Não mudar permissões antes da resposta.

O código de produção continua f669ce2, com CI anterior de 688 passed, 3 skipped,
0 failed. Esta etapa adiciona evidência manual e SQL de diagnóstico, não uma nova
execução de pytest nem um novo deploy. git diff --check deve passar antes do commit.

Evidências nos outputs: E2E_BREGUET_APOLO.jpg, E2E_HISTORICO_APOLO.jpg,
E2E_SUPABASE_RESULTADOS_APOLO.jpg, E2E_OPERADOR_AUTORIZACAO_APOLO.jpg,
E2E_LOGOUT_APOLO.jpg, E2E_LOGIN_NEGADO_APOLO.jpg.
A habilidade de uso do computador orientou a conferência do aplicativo/painel
no navegador e a coleta de evidências sem extrair credenciais.
