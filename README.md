# Apolo Web

Seis cálculos e 23 variáveis do Apolo 2.6.0, preservados em core matemático puro.
Streamlit usa serviços com autorização e repositories SQLite ou Supabase.
Auth, PostgreSQL/RLS, projetos e deploy Render estão preparados em código.
**CI remota e fluxo real Supabase/Render ainda precisam de validação.**

## Rodar localmente com SQLite

Python 3.12, na raiz:

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
    $env:APOLO_ENV='development'
    $env:APOLO_AUTH_MODE='local'
    $env:APOLO_REPOSITORY_MODE='sqlite'
    $env:APOLO_LOCAL_ROLE='operador'
    .\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1

Ou iniciar.ps1 -Perfil operador/admin/desenvolvedor. O iniciador usa somente
venv própria ou Python do sistema. APOLO_DATA_DIR permite outra pasta gravável.
Sem bancos, cria novo SQLite. Selecionar arquivos não mescla históricos.

Provider local é identidade de teste, não login; não exponha esse modo na internet.
originals, data, venv, .env e secrets ficam fora do Git.

## Modo online

Primeiro configure projeto Supabase dedicado e aplique, em ordem e uma vez,
as três migrations em supabase/migrations. Crie contas de teste pelo painel Auth;
profiles começam como operadores. Papel não vem de metadata editável pelo usuário.
Veja detalhes e checklist no manual antes de conectar dados reais.

    $env:APOLO_ENV='production'
    $env:APOLO_AUTH_MODE='supabase'
    $env:APOLO_REPOSITORY_MODE='supabase'
    $env:SUPABASE_URL='<URL HTTPS do projeto>'
    $env:SUPABASE_PUBLISHABLE_KEY='<publishable key>'
    $env:PORT='10000'
    .\.venv\Scripts\python.exe -m tools.iniciar_online

Para ensaio online só em localhost, use development e Streamlit diretamente.
.env.example documenta opções; .env não é carregado automaticamente.
Nunca usar service_role/sb_secret. Senhas e tokens não entram no código/chat/Git.

Usuários autenticados criam/selecionam projetos próprios, calculam e consultam
histórico. ADMIN configura o próprio projeto; DESENVOLVEDOR também diagnostica.
Serviço e banco verificam permissões; ocultar página não é a proteção.
Sessão vale para a conexão Streamlit; novo acesso/reinício pode exigir login.

## Testar

    .\.venv\Scripts\python.exe -m pytest tests -q

A suíte não depende de originals/data. Mantém 600 comparações exatas em JSON,
seis referências independentes, cinco inválidos Breguet e NaN/inf/overflow.
Auditorias históricas são opcionais. Não é necessário regenerar fixtures.

Marco 663bd2c: usuário confirmou 640 passed ou 637 passed, 3 skipped portátil.
Novo marco: runner diagnóstico observou **680 passed, 11 skipped, 0 failed**;
há limitação de temporários do sandbox, por isso a execução padrão está pendente.
Onze skips: três históricos e oito PostgreSQL. APIs controladas não provam
Auth/RLS reais. Actions foi preparado com PostgreSQL 16 para executar SQL/RLS.

Para testes SQL locais, instale requirements-dev e aponte
APOLO_TEST_POSTGRES_DSN somente para PostgreSQL descartável vazio com
APOLO_TEST_POSTGRES_ISOLATED=1. Não use banco Supabase existente/produção:
o bootstrap cria auth.users/auth.uid e roles de teste.

## Render

render.yaml prepara serviço free, auto-deploy desligado e branch
feature/render-deploy. Configure URL/publishable key no painel e confirme CI verde.
Build: python -m pip install -r requirements.txt
Start: python -m tools.iniciar_online
Health: /_stcore/health; endereço 0.0.0.0 e porta PORT.
Não há banco/disco Render: persistência fica no Supabase.
Health verde não confirma Auth/banco; siga a validação real do manual.

## Importação local do legado

    .\.venv\Scripts\python.exe -m tools.importar_banco 'C:\caminho\Banco.db' --audit-only
    $env:APOLO_ENV='development'
    $env:APOLO_AUTH_MODE='local'
    $env:APOLO_REPOSITORY_MODE='sqlite'
    $env:APOLO_LOCAL_ROLE='desenvolvedor'
    .\.venv\Scripts\python.exe -m tools.importar_banco 'C:\caminho\Banco.db' --nome Projeto.db

Valida schema/catálogo/integridade e cria cópia nova. Não modifica origem.
Não foi implementada migração automática de dados locais para o banco online.

## Organização e documentação

- core: matemática/catálogo, sem Streamlit/Supabase/Render.
- services: casos de uso e autorização.
- database: contrato, SQLite e Supabase.
- auth/integrations: identidade, sessão e transporte HTTPS.
- interface: formulários e apresentação.
- supabase/migrations: tabelas, catálogo, grants/RLS/RPC.
- tools/tests: iniciadores, auditorias e regressão.

MANUAL_TECNICO_APOLO_WEB_IMPLEMENTADO.md ensina arquitetura e todas as mudanças.
CHANGELOG_IMPLEMENTACAO.md registra etapas, commits, evidências e pendências.
AUDITORIA.md/auditoria.json são referências históricas, não certificação online.
Fórmulas/unidades não foram ampliadas: Breguet retorna metros e usa consumo em s⁻¹.
