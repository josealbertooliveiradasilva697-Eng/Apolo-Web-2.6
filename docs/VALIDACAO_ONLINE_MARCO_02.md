# Validação online — marco 02

Data: 03/10/2026. Código validado: f669ce255af3a2110f08597ab5e98afb5c922c5a.
Registro sem senhas, tokens ou valores de chaves.

## Suíte padrão e publicação confirmadas

O usuário executou IMPORTAR_MARCO_02.ps1 no terminal normal:

- Clone original com ativos históricos: **683 passed, 8 skipped**, 16,70 s.
- Cópia sem originals/data: **680 passed, 11 skipped**, 22,11 s.
- Develop local integrado por fast-forward; main e ativos locais preservados.
- feature/render-deploy publicada no GitHub e configurada para acompanhar origin.
- Backups: backup/pre-online-20261003-185811 e
  backup/develop-pre-online-20261003-185811.

Isso resolve a pendência de pytest padrão do novo marco. As limitações de
temporários do sandbox permanecem históricas, não invalidam o teste padrão recebido.

## CI real conferida no navegador

[Execução 37156911993](https://github.com/josealbertooliveiradasilva697-Eng/Apolo-Web-2.6/actions/runs/37156911993)
concluída com sucesso para f669ce2.

[Job pytest e log](https://github.com/josealbertooliveiradasilva697-Eng/Apolo-Web-2.6/actions/runs/37156911993/job/111302058076)
confirmou **688 passed, 3 skipped em 6,22 s**. Job: 58 s; execução: 1 min 2 s.
Oito testes PostgreSQL foram executados, não pulados. Validaram migrations,
grants, RLS, papéis, isolamento, rollback e persistência de 600 snapshots.
Três skips: auditorias históricas opcionais sem arquivos privados.

Auth/users/uid do bootstrap são stubs; PostgreSQL/transações/RLS são reais.
Isso não substitui teste de sessão no Supabase Auth real.

Avisos não impeditivos do GitHub: setup-python@v5 usa Node 20 e foi forçado
a Node 24; ubuntu-latest anuncia mudança de imagem. A CI passou. Atualizar
ações/pinar runner será decisão separada, sem confundir aviso com regressão.

## Supabase instalado com autorização explícita

Organização: Alberto Engenharia. Projeto dedicado confirmado pelo usuário:
josealbertooliveiradasilva697-Eng's Project, referência yujvliymyyvbyzwmrrts.
O schema public estava sem tabelas/views antes da instalação.
Não houve exclusão, migração de dados SQLite nem contratação de plano pago.

Aplicadas uma vez, em ordem, pelo SQL Editor:

1. 202610030001_schema.sql;
2. 202610030002_catalog.sql;
3. 202610030003_security_rpc.sql.

Cada conteúdo foi copiado do arquivo versionado e conferido integralmente
contra o editor antes de executar. O editor retornou sucesso.
Como a aplicação foi manual, não se afirma que o histórico automático
supabase_migrations registrou essas versões; este documento é o registro.

A consulta somente leitura supabase/verificacoes/20261003_instalacao.sql
confirmou:

| Campo | Resultado |
| --- | --- |
| variaveis | 23 |
| calculos | 6 |
| dependencias | 30 |
| tabelas | 8 |
| tabelas_rls | 8 |
| politicas_rls | 9 |
| anon_sem_leitura | true |
| cliente_sem_update_direto | true |
| anon_sem_rpc | true |
| autenticado_pode_rpc | true |

Não reaplicar as migrations. Consultas de auditoria são repetíveis.
Não usar o bootstrap pytest de PostgreSQL contra esse projeto Supabase.

## Render publicado e conferido

Serviço apolo-web, ID srv-db0o97favr4c738kgleg, no plano Free (US$ 0/mês),
Ohio. Nenhuma assinatura paga ou armazenamento local foi contratado.
Repositório privado já autorizado no Render; branch feature/render-deploy,
commit f669ce2. Não foram concedidas novas permissões OAuth.

Deploy dep-db0o97navr4c738kgne0: **Deploy succeeded | Live**, duração 1 min 2 s,
iniciado em 03/10/2026 às 19:41:34 GMT-3.
[Registro do deploy](https://dashboard.render.com/web/srv-db0o97favr4c738kgleg/deploys/dep-db0o97navr4c738kgne0).

Configuração aplicada no painel:

- Python 3.12.10; build: python -m pip install -r requirements.txt.
- Start: python -m tools.iniciar_online; health: /_stcore/health.
- Auto-deploy desativado; root directory vazio (raiz do repositório).
- APOLO_ENV=production, APOLO_AUTH_MODE=supabase,
  APOLO_REPOSITORY_MODE=supabase.
- SUPABASE_URL do projeto aprovado e sua chave publishable existente,
  configuradas somente no ambiente Render. Sem service_role ou senha PostgreSQL.
- PORT fornecida pelo Render; processo na porta 10000.

O navegador abriu [Apolo Web](https://apolo-web-z74k.onrender.com/) e exibiu
“Apolo · Cálculos Aerodinâmicos”, “Base 2.6.0”, formulário E-mail/Senha/Entrar.
Nenhuma exceção de configuração ou tela SQLite foi apresentada.
Isso confirma inicialização em produção e login acessível; não confirma login
bem-sucedido ou uma operação no banco, que exigem contas reais.
O deploy passou a checagem interna de saúde do Render. A tentativa de visitar
diretamente /_stcore/health foi bloqueada pelo cliente do navegador;
não desativamos proteção para contornar isso.

Evidências fora do repositório: CI_MARCO_02.jpg,
SUPABASE_AUDITORIA_INSTALACAO.jpg, RENDER_DEPLOY_APOLO.jpg,
RENDER_LOGIN_APOLO.jpg. Não contêm senhas/tokens.

## Ponto de passagem para o usuário e pendências reais

O painel Supabase Authentication/Users apresentou erro de tradução automática
do Edge (insertBefore). O schema já foi instalado e auditado antes desse erro;
não repetir migrations. Desativar a tradução da página e atualizar o painel.

Solicitado ao usuário: criar **duas contas de teste** em Authentication → Users →
Add user → Create new user, com e-mail confirmado automaticamente, escolhendo
e digitando as próprias senhas. Não enviar senhas/tokens no chat.
Depois entrar no Apolo publicado com a primeira conta e avisar que está pronto.
O novo profile deve nascer OPERADOR; não promover papéis por metadata do cliente.
Promoções para testar ADMIN/DESENVOLVEDOR exigem ação administrativa delimitada.

Ainda falta validação real de login/logout/refresh, perfis, dois usuários,
projetos, seis cálculos, histórico, isolamento via API, restart e redeploy.
Chaves administrativas não são utilizadas pelo aplicativo.
Um grant seguro conferido não é, sozinho, validação completa de isolamento
numa conta real. Registrar as próximas evidências antes de declarar conclusão.
