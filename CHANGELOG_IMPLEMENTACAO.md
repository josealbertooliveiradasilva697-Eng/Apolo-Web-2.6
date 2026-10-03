# Changelog da implementação Apolo Web

## 03/10/2026 — Marco 1: portabilidade e preparação de CI

Status: arquivos e testes diagnósticos preparados; commit bloqueado por permissão
de .git. Nenhum merge, push ou deploy.

Branch: feature/ci-portable-tests.
Baseline: a4cd61af479430c471c2140d1d5867a511ed606b.
Commit confirmado pelo usuário e pelo histórico local: **663bd2c**.
Mensagem:
`test: tornar referencias do legado portateis e preparar CI`.
Suíte padrão confirmada pelo usuário: **640 passed** no clone e
**637 passed, 3 skipped** na cópia portátil. CI remota ainda pendente.

## 03/10/2026 — Etapa 2: estabilização local

Branch: feature/local-stabilization, criada de develop após integrar 663bd2c.
Arquivos: iniciar.ps1, .gitignore, README.md e documentação.
Motivo: retirar caminhos de sessão Codex e instruções dependentes de bancos
específicos; proteger arquivos .env alternativos e dados locais.
Dependências mantidas em suas versões verificadas; nenhum dado real copiado.
Verificação diagnóstica da suíte: **637 passed, 3 skipped**.
Commit correspondente: **49f602f**.

## 03/10/2026 — Etapa 3: contrato de persistência

Branch: feature/supabase-database, a partir de develop.
Arquivos: database/contracts.py, database/repository.py, services/apolo.py,
interface/telas.py e tests/test_contrato_persistencia.py.
Contrato inclui somente operações usadas e uma identidade de contexto.
SQLite mantém schema e transações. Diagnósticos passaram pelo serviço autorizado.
Dois testes verificam execução sem arquivo e autorização fora da tela.
Suíte diagnóstica: **639 passed, 3 skipped**. Commit: **40d863c**.

## 03/10/2026 — Etapas 4 e 6: persistência Supabase e RLS

Branch: feature/supabase-database.
Criados: config.py, integrations/supabase_http.py, database/supabase_repository.py,
services/projects.py, três migrations SQL, tests/test_supabase_repository.py
e tests/test_postgres_integracao.py.
Alterados: .env.example e requirements-dev.txt (psycopg só para testes reais).
Motivo: persistência com JWT individual, projetos privados e RPC atômico;
cadastros sempre operadores; nenhuma escrita direta em perfis/valores/histórico.
Teste de contrato REST: suíte diagnóstica **652 passed, 3 skipped**, antes de
acrescentar os oito testes PostgreSQL opcionais.
PostgreSQL/Auth real ainda não configurados. SQL/RLS precisam de execução real.

| Etapa | Arquivos | Motivo | Testes |
| --- | --- | --- | --- |
| 1 | tests/test_equivalencia.py | Referências JSON; cardinalidade/seeds/SHA; auditoria local. | 600 comparações, seis referências, cinco inválidos, NaN/inf/overflow, AST/SHA. |
| 1 | tests/test_banco_e_papeis.py | Schema auditado sem originals obrigatório. | 11 objetos/SHA e testes de banco/papéis preservados. |
| 1 | tests/test_bancos_reais.py | Skip individual por banco ausente. | Dois testes locais; ambos pulados na cópia portátil. |
| 1 | tests/fixtures/*.json; tools/gerar_fixtures_legado.py | Preparar arquivos recebidos não versionados para commit. | 600 casos, cinco inválidos, 11 objetos, SHA conferidos. |
| 8, preparação antecipada | .github/workflows/tests.yml | CI em Python 3.12 sem dados privados. | Arquivo preparado; execução remota pendente. |
| Documentação | README.md; manual; changelog | Explicar decisões/evidências/limitações. | Conferidos contra o estado real. |

Resultados após os ajustes:

- Clone real, runner diagnóstico: **640 passed, 0 skipped, 0 failed**.
- Cópia sem originals/data, runner diagnóstico: **637 passed, 3 skipped, 0 failed**.
- pytest padrão inicial no sandbox: **620 passed, 20 errors** de setup por
  permissões de temporários; não conta como aprovação completa.
- pytest padrão fora do sandbox e GitHub Actions: pendentes.
- Interface validada por AppTest; nenhum teste manual no navegador neste marco.

Runner auxiliar fora do repo substitui somente tmp_path por diretórios com ACL
herdada; não modifica ACL, testes ou bibliotecas. Há erro de limpeza de
TemporaryDirectory na saída do processo do sandbox.

Permissão de escrita no repo/.git foi concedida, mas Git continuou sem criar
index.lock. Clones independentes também falharam por restrição de sh/signal pipe.
Roteiro manual de validação/commit foi entregue. Fórmulas, catálogo, schema,
main/develop, originals/data permanecem preservados.

Migrations: nenhuma. Dependências alteradas: nenhuma.
Supabase, Auth, RLS, Render e validação online: pendentes.

## Próximo marco

Confirmar testes padrão e commit; registrar o hash; integrar em develop e iniciar
estabilização/contrato de persistência em features adequadas.

## 03/10/2026 — Etapas 5 e 7: Auth e interface online

Branch: feature/supabase-auth, criada de develop após bce8338.
Criados: auth/supabase_provider.py, tests/test_supabase_auth.py,
tests/test_interface_online.py. Alterados: app.py, auth/provider.py, config.py,
iniciar.ps1, interface/telas.py e tests/test_supabase_repository.py.
Motivo: validar identidade no Auth, renovar sessão, obter papel protegido,
usar projetos privados e impedir autenticação fictícia em produção.
Testes: login/refresh/logout, perfis negados, erros de rede, seis cálculos,
histórico, criação de projeto e ausência de arquivo SQLite no modo online.
Suíte diagnóstica: **671 passed, 11 skipped, 0 failed**. Os skips são três
auditorias históricas e oito integrações que exigem PostgreSQL dedicado.
Sem validação em conta Supabase/Render real até este momento.

## 03/10/2026 — Etapas 8 e 9: PostgreSQL na CI e preparo Render

Branch: feature/render-deploy, a partir de develop após c00bdad.
Criados: render.yaml, tools/iniciar_online.py e tests/test_render_deploy.py.
Alterados: .github/workflows/tests.yml e .env.example.
Motivo: CI com PostgreSQL 16 descartável e testes reais de grants/RLS/transações;
servidor com bind 0.0.0.0, PORT validada, sem persistência local e sem provider fake.
Teste de fumaça: servidor local e iniciador de produção responderam
**ok** em /_stcore/health; processos de teste encerrados.
O primeiro teste do iniciador detectou problema de quoting do execv no Windows;
corrigido usando subprocess com lista de argumentos apenas nessa plataforma.
Suíte diagnóstica final desta etapa: **680 passed, 11 skipped, 0 failed**.
As 600 referências matemáticas continuam intactas.
CI/deploy reais não executados: HTTPS Git bloqueado por credenciais Schannel
e cadeia de certificados indisponível na alternativa OpenSSL. TLS não foi desabilitado.
