# Publicação da correção administrativa — 03/10/2026

Atualização posterior: usuário executou o verificador com duas contas reais;
isolamento HTTP nas duas direções, RPC 403 e refresh real aprovados, logout local
confirmado. Veja VALIDACAO_API_SESSAO.md. Pendências API/refresh abaixo são
históricas; consolidação Git/CI do novo tip e limites operacionais permanecem.

## Suíte padrão e CI

O usuário importou/publicou feature/config-form-state no clone original, em
2486215218c17f770ba804012ccb3b19434e5579. Pytest padrão: **691 passed, 8 skipped,
0 failed**, 21,38 s. Backup informado: backup/pre-correcao-config-20261003-214050.
Conferência read-only: árvore limpa; main a4cd61a, develop f669ce2 preservadas.

[Actions 37165709281](https://github.com/josealbertooliveiradasilva697-Eng/Apolo-Web-2.6/actions/runs/37165709281)
aprovado para 2486215: **696 passed, 3 skipped, 0 failed**, 8,55 s.
Job 111328048280 executou os oito testes PostgreSQL 16 reais e as oito novas
regressões do formulário. Os três skips são auditorias locais ausentes na CI;
os oito skips locais exigem PostgreSQL dedicado. Não houve redução da cobertura.

## Novo deploy

Render Free, serviço srv-db0o97favr4c738kgleg. Selecionado **Deploy a specific
commit**, SHA completo 2486215 acima, após conferir a CI. Deploy
dep-db0q69k9v7es73ciivp0: **Deploy succeeded|Live**, 1 min 3 s, iniciado às
21:51:50 GMT-3 em 03/10/2026. Build e health interno aprovados.

URL: https://apolo-web-z74k.onrender.com/.
Detalhe: https://dashboard.render.com/web/srv-db0o97favr4c738kgleg/deploys/dep-db0q69k9v7es73ciivp0.
Tela pública de login conferida após recarregar o app. Nenhuma migration
reaplicada, assinatura contratada, credencial extraída ou proteção desativada.

A configuração continua feature/render-deploy, auto-deploy off. A versão Live
é o SHA específico 2486215, apesar do nome da branch no cabeçalho/log do Render.
**Deploy latest commit** dessa branch pode voltar ao código antigo f669ce2 até
a integração/publicação correspondente. Sempre conferir Source, não só a branch.
Rollback disponível no deploy anterior dep-db0o97navr4c738kgne0.

## Dados e teste autenticado

Consulta independente 20261003_estado_ui.sql após o deploy confirmou
OPERADOR / Conectado com sucesso / seis execuções no projeto E2E A.
A auditoria 20261003_e2e.sql confirmou A com seis cálculos distintos, 30 snapshots,
23 variáveis e seis resultados equivalentes (tolerância 1e-12); B com zero
execuções e 23 variáveis. Três profiles OPERADOR antes do reteste.
O deploy reinicia o processo, não migra o banco; a sessão Streamlit anterior
terminou e novo login é necessário. Isso não demonstra refresh de token.

Revalidação do segundo envio na UI real aprovada. O usuário entrou e autorizou
temporariamente DESENVOLVEDOR na conta indicada, restaurando texto e OPERADOR
ao terminar. Promoção condicionada ao UUID/e-mail/papel OPERADOR e exatamente
uma linha atualizada; SQL e UI confirmaram DESENVOLVEDOR, somente no projeto A.
Sem sair/recarregar a página, status_projeto recebeu o primeiro texto
`Validacao correcao primeiro envio 2026-10-03`, depois
`Validacao correcao segundo envio 2026-10-03`. Após CADA envio, consulta independente
confirmou o texto correspondente e seis execuções. Terceiro envio restaurou
`Conectado com sucesso`, também confirmado no SQL. Não houve novo cálculo.
Esse teste usa Auth/PostgREST reais, complementando os oito AppTest controlados.
OPERADOR restaurado e confirmado no SQL; rerun revalidou o perfil e removeu
Administração/Diagnósticos da navegação. Histórico real abriu os registros
originais após o deploy, incluindo execução da86637e-7494-4435-ab69-bb1a24ad593b.

## Reinício separado

Após restauração, usado Manual Deploy -> Restart service, sem novo build ou
troca de SHA. Render confirmou “Your server has successfully restarted”.
App retornou à tela de login. Consulta estado_ui depois do restart:
OPERADOR / Conectado com sucesso / seis execuções. Usuário fez novo login;
projeto A/histórico abriu com os mesmos seis IDs, todos SUCESSO. Screenshot
conferida visualmente. Auditoria e2e repetida após restart confirmou seis
equivalências, 30 snapshots, 23 variáveis, B vazio e três profiles OPERADOR.

Pendentes: acesso cruzado negativo pela API
com JWTs reais e refresh real. Verificador interativo entregue em outputs,
reutilizando Auth/HTTP do app, sem alteração de dados. Oito testes simulados do
roteiro aprovados; execução com credenciais pelo usuário ainda pendente.
Refresh será acionado pelo relógio do cliente, não pela expiração natural do JWT.
Instalação SQL/RLS, papéis e seis cálculos reais já têm registros anteriores.

## Git e evidências

Após CI/deploy aprovados, correção integrada por fast-forward ao develop SOMENTE
no clone isolado (2486215). Registro criado na feature/production-validation,
a partir desse develop. Main e develop do OneDrive não foram alteradas pelo agente.
Nenhuma alteração nova de runtime, fórmula, fixture, dependência ou migration.

Criado este documento; alterados manual/changelog e registro da correção para
separar evidência histórica de estado atual. Conferência: git diff --check.
Sem nova execução pytest para esta mudança exclusivamente documental; os
resultados acima pertencem ao mesmo código de produção 2486215.
Evidências em outputs: CI_CORRECAO_CONFIGURACAO.jpg e
RENDER_CORRECAO_CONFIGURACAO.jpg. Hash documental no relatório entregue.
Acrescentadas: E2E_CORRECAO_SEGUNDO_ENVIO_APOLO.jpg e
E2E_CORRECAO_SQL_SEGUNDO_ENVIO.jpg.
Também E2E_HISTORICO_POS_DEPLOY.jpg e RENDER_REINICIO_CORRECAO.jpg.
E2E_HISTORICO_POS_REINICIO.jpg confirma operador/projeto A/seis registros reais.
