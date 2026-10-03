# Changelog da implementação Apolo Web

## Validação real do operador — continuação da etapa 10

Branch: feature/online-validation; código publicado permanece f669ce2.
Login real OPERADOR confirmado; criados projetos A/B exclusivos de teste.
As seis equações foram salvas pela UI Render, com referências independentes.
Supabase confirmou seis execuções, 30 snapshots, 23 variáveis por projeto e
as seis saídas equivalentes (1e-12). Breguet inválido não criou execução.
Histórico/detalhes, separação A/B, banco de variáveis, logout e login inexistente
foram conferidos no navegador. Teste SQL real com claims controlados negou
configuração/diagnóstico ao operador (42501), com rollback e sem promoção de papel.
Não afirmar isolamento HTTP entre usuários: a auditoria encontrou só um perfil.
Pendente segunda conta e autorização para teste temporário ADMIN/DESENVOLVEDOR.
Criados: docs/VALIDACAO_E2E_OPERADOR.md,
supabase/verificacoes/20261003_e2e.sql, supabase/verificacoes/20261003_operador.sql.
Alterados: manual/changelog e registro online anterior.
Sem alterações estruturais/runtime; git diff --check e SQL executado no banco real.
CI de referência: 688 passed, 3 skipped, 0 failed para f669ce2 (não rerodada agora).
Commit: assunto “docs: registrar fluxo real de operador e persistencia online”;
hash no relatório externo. Main/develop/Render e dados originais preservados.

## Confirmação posterior — suíte padrão, CI e instalação Supabase

Branch de registro: feature/online-validation, criada de develop em f669ce2.
Usuário confirmou pytest padrão: **683 passed, 8 skipped** no clone original;
**680 passed, 11 skipped** portátil. feature/render-deploy foi publicada.
CI 37156911993 aprovada: **688 passed, 3 skipped**, incluindo oito testes
PostgreSQL reais. Migrations 001/002/003 aplicadas com autorização explícita
no projeto Supabase dedicado. Auditoria: 23 variáveis, seis cálculos,
30 dependências, oito tabelas com RLS, nove policies e grants restritos.
Criados: docs/VALIDACAO_ONLINE_MARCO_02.md e
supabase/verificacoes/20261003_instalacao.sql. Sem alteração de fórmulas.
As pendências de CI/SQL/padrão nos registros abaixo descrevem o marco anterior;
foram resolvidas pelas evidências acima. Render Free publicado: serviço
srv-db0o97favr4c738kgleg, deploy dep-db0o97navr4c738kgne0 aprovado em 1 min 2 s;
tela de login conferida em https://apolo-web-z74k.onrender.com/.
Auto-deploy off; nenhuma assinatura paga, chave administrativa ou dado legado.
Teste autenticado real aguarda duas contas criadas pelo usuário, sem senhas no chat.
Commit de registro: consultar git log pelo assunto
“docs: registrar CI verde e implantacao Supabase Render”; hash no relatório externo.

Data: 03/10/2026. Baseline preservada: a4cd61a.
Código até f669ce2 importado no OneDrive e publicado pelo usuário.
Documentação desta confirmação está na feature/online-validation do clone isolado.

## Commits e integração

| Etapa | Branch a partir de develop | Commit | Resultado |
| --- | --- | --- | --- |
| 1: testes portáteis/CI inicial | feature/ci-portable-tests | 663bd2c | 640 passed padrão com ativos; 637 passed, 3 skipped portátil, confirmados pelo usuário |
| 2: estabilização local | feature/local-stabilization | 49f602f | 637 passed, 3 skipped diagnóstico |
| 3: contrato de persistência | feature/supabase-database | 40d863c | 639 passed, 3 skipped diagnóstico |
| 4/6: PostgreSQL/Supabase/RLS | feature/supabase-database | bce8338 | 652 passed, 11 skipped diagnóstico; SQL real ainda pulado |
| 5/7: Auth e UI online | feature/supabase-auth | c00bdad | 671 passed, 11 skipped diagnóstico |
| 8/9: CI PostgreSQL/Render | feature/render-deploy | 2ba3979 | 680 passed, 11 skipped diagnóstico + health ok |

Cada feature foi integrada por fast-forward ao develop isolado antes da seguinte.
Main não foi alterada. O usuário publicou feature/render-deploy sem force;
Supabase instalado com aprovação explícita e Render Free publicado depois da CI.
Não foi aberto PR nem publicado develop remoto.
A atualização final de documentação é commit separado na feature/render-deploy;
seu hash está no relatório do pacote e em git log --oneline.

## Etapa 1 — Portabilidade

Arquivos: tests/test_equivalencia.py, tests/test_banco_e_papeis.py,
tests/test_bancos_reais.py, tests/fixtures/equivalencia_apolo_26.json,
tests/fixtures/schema_apolo_26.json, tools/gerar_fixtures_legado.py,
.github/workflows/tests.yml, README.md e os dois documentos obrigatórios.
Motivo: CI não recebe originals/data; JSON auditado conserva cobertura.
Testes: 600 equivalências, seis números independentes, cinco Breguet inválidos,
NaN/inf/overflow, 11 objetos de schema, seeds/cardinalidade/SHA e auditorias opcionais.
Commit 663bd2c, produzido pelo usuário com roteiro do marco anterior.
Não houve redução da cobertura de equivalência.

## Etapa 2 — Limpeza

Arquivos: iniciar.ps1, .gitignore, README.md e documentação.
Motivo: remover referência à venv de sessão Codex, proteger toda data e variantes
.env e descrever instalação reproduzível. Runtime permaneceu igual.
Testes: suíte local portátil e interface existentes. Commit 49f602f.

## Etapa 3 — Persistência desacoplada

Arquivos: database/contracts.py, database/repository.py, services/apolo.py,
interface/telas.py e tests/test_contrato_persistencia.py.
Motivo: serviço usa contrato real pequeno; tela usa contexto, não arquivo;
diagnóstico passa pela autorização do serviço.
Testes novos: repository em memória sem path e acesso negado fora da interface.
Commit 40d863c. Schema SQLite, catálogo e fórmulas inalterados.

## Etapas 4 e 6 — Schema, API e segurança

Criados: config.py, integrations/__init__.py, integrations/supabase_http.py,
database/supabase_repository.py, services/projects.py,
tests/test_supabase_repository.py, tests/test_postgres_integracao.py e:
- supabase/migrations/202610030001_schema.sql;
- supabase/migrations/202610030002_catalog.sql;
- supabase/migrations/202610030003_security_rpc.sql.

Alterados: .env.example, requirements-dev.txt e documentação.
Motivo: oito tabelas com dono/projeto; catálogo estável; JWT individual;
RLS/grants; perfil operador por default; RPC atômica de histórico/valores.
Auth fake não é aceito em produção. Secret/service_role rejeitadas.
psycopg[binary]==3.3.6 é driver de testes, não dependência de produção.
Testes REST/config: operação única de salvar, contexto, catálogo completo,
credenciais inadequadas, sessão/rede/HTTP seguros. Oito testes SQL opcionais
incluem roles, cross-user, self-promotion negada, rollback e 600 snapshots.
Commit bce8338. Migrations foram escritas, não aplicadas em Supabase real.

## Etapas 5 e 7 — Sessão e interface online

Criados: auth/supabase_provider.py, tests/test_supabase_auth.py,
tests/test_interface_online.py.
Alterados: app.py, auth/provider.py, config.py, iniciar.ps1,
interface/telas.py, tests/test_supabase_repository.py e changelog.
Motivo: login, refresh/logout, identidade confirmada por /auth/v1/user,
profile protegido, projetos privados e remoção de SQLite no caminho online.
Testes: perfil faltante/errado, metadata não autoriza, refresh revogado,
falha de rede distinta de credencial inválida, logout/limpeza,
seis formulários numéricos, histórico e criação de projeto com API controlada.
Commit c00bdad. Não houve cadastro público, cookie persistente ou gestão global.

## Etapas 8 e 9 — CI e Render

Criados: render.yaml, tools/iniciar_online.py, tests/test_render_deploy.py.
Alterados: .github/workflows/tests.yml, .env.example e changelog.
Motivo: CI com PostgreSQL 16 dedicado, porta Render validada, 0.0.0.0,
startup exige produção/Supabase, sem disco local ou contratação paga.
Teste de fumaça detectou quoting de execv no Windows com espaços no caminho.
Correção: subprocess com lista de argumentos no Windows; execv no Linux.
Novos testes protegem portas inválidas, configuração local, argumentos com espaços
e campos mínimos do template. Não equivalem à validação do Blueprint no Render.
Health local e startup online de exemplo responderam ok; processos encerrados.
Commit 2ba3979. A confirmação posterior está no início deste documento:
CI e deploy remotos passaram para f669ce2, sem alterar o código dessa etapa.

## Documentação final

Manual reescrito com 31 seções: antes/depois, fluxos, oito tabelas, policies/RPCs,
arquivos, testes, variáveis, modos, deploy, diagnóstico, limitações e Apolo 3.
README atualizado com ambos os modos e resultados observados.
auth/provider.py: mensagem do helper local aponta para ProvedorSupabase,
em vez de afirmar incorretamente que Auth ainda não está implementado.
Este changelog substitui os estados “planejados” dos marcos anteriores.
Fora do repo: relatório, bundle, ZIP de código e script seguro de importação/publicação.
Não são dependências de runtime.

## Evidências e limites

Resultado diagnóstico final: **680 passed, 11 skipped, 0 failed**, 15,18 s.
Três skips de ativos históricos ausentes; oito de PostgreSQL sem DSN.
Runner externo substitui só tmp_path e não modifica ACL/testes/bibliotecas.
Ainda há erro de cleanup de TemporaryDirectory ao sair do sandbox.
Essa limitação histórica foi superada por pytest padrão no terminal do usuário
e GitHub Actions, sem alterar ACLs ou flexibilizar TLS.

Validações realizadas: AppTest local/online, dois testes HTTP locais, pytest padrão,
CI PostgreSQL/RLS real, auditoria SQL Supabase, deploy e tela pública de login.
Não realizadas: login/Auth/PostgREST reais com contas, reinício/novo deploy
com histórico persistido. Proteções SQL instaladas não substituem esses testes.

Git HTTPS: Schannel sem credenciais; alternativa OpenSSL com cadeia de
certificados indisponível. Não desabilitamos TLS nem extraímos credenciais.
Secrets, dados legados e arquivos de banco não foram versionados.
Pendência imediata: usuário criar duas contas confirmadas e entrar no aplicativo;
depois executar checklist autenticado do manual. Tradução automática do Edge
causou erro no painel Users; solicitar desativação da tradução e atualização,
sem contornar segurança ou repetir migrations.
