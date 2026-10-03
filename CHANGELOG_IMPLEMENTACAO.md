# Changelog da implementação Apolo Web

## 03/10/2026 — Marco 1: portabilidade e preparação de CI

Status: arquivos e testes diagnósticos preparados; commit bloqueado por permissão
de .git. Nenhum merge, push ou deploy.

Branch: feature/ci-portable-tests.
Baseline: a4cd61af479430c471c2140d1d5867a511ed606b.
Commit: **pendente**; mensagem proposta:
`test: tornar referencias do legado portateis e preparar CI`.
Registrar o hash real após o commit bem-sucedido.

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
