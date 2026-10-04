# Manual técnico do Apolo Web implementado

Continuação autenticada: segunda conta conferida, isolamento real por SQL/RLS e
telas ADMIN/DESENVOLVEDOR aprovados. A única conta promovida temporariamente
voltou a OPERADOR, com remoção das páginas privilegiadas no rerun. Projeto A:
status_projeto original restaurado e seis execuções preservadas.
Veja docs/VALIDACAO_PAPEIS_ISOLAMENTO.md. Identificado defeito em dois salvamentos
consecutivos de configuração, reproduzido por quatro regressões. Correção,
publicação, API negativa, refresh e restart/redeploy pendentes.
Os parágrafos seguintes registram a sequência histórica das validações.

Validação real posterior: login OPERADOR, seis cálculos persistidos, 30 snapshots,
separação de dois projetos, histórico, banco de variáveis, Breguet inválido,
logout e login negativo aprovados. SQL no Supabase negou configuração/diagnóstico
ao operador dentro de transação com rollback. Auditoria encontrou um perfil;
segunda conta, papéis privilegiados, refresh/restart/redeploy ainda pendentes.
Veja docs/VALIDACAO_E2E_OPERADOR.md. Não houve promoção de papel nesta etapa.

Atualização posterior ao marco f669ce2: o usuário confirmou a suíte padrão
(683 passed, 8 skipped com ativos; 680 passed, 11 skipped portátil).
Actions 37156911993 foi conferido e passou com **688 passed, 3 skipped**,
executando os oito testes PostgreSQL reais. Após autorização explícita,
as três migrations foram instaladas no Supabase dedicado e a auditoria
confirmou 23 variáveis, seis cálculos, oito tabelas com RLS e nove políticas.
Veja docs/VALIDACAO_ONLINE_MARCO_02.md e a consulta repetível em
supabase/verificacoes/20261003_instalacao.sql. Os estados “pendentes” abaixo
registram o momento anterior à publicação; CI/pytest/instalação SQL já foram
confirmados. Render publicado no plano gratuito, deploy aprovado e tela de login
conferida em https://apolo-web-z74k.onrender.com/. Login/cálculos reais foram
validados; isolamento entre usuários via API ainda exige segunda conta.

Atualizado em 03/10/2026. Código preparado até PostgreSQL/Auth/RLS/UI/CI/Render.
**A validação de produção ainda não está concluída:** CI e instalação SQL já
passaram; fluxo OPERADOR aprovado, mas faltam segunda conta, papéis privilegiados,
refresh real e validação de persistência após restart/redeploy.

Este manual explica o que mudou e por quê. Não confunde um teste com API simulada
com um teste no serviço real. As fórmulas e o schema SQLite não foram alterados.

## 1. Estado inicial recebido e pontos de retorno

Baseline: a4cd61a, “Baseline inicial do Apolo Web”. O usuário confirmou o marco
663bd2c com pytest padrão: 640 passed no clone e 637 passed, 3 skipped sem os
ativos históricos. A portabilidade preservou as 600 comparações exatas,
seis resultados independentes, cinco inválidos de Breguet e NaN/inf/overflow.

O projeto já separava interface, serviços, matemática, identidade e SQLite.
Havia seis cálculos, 23 variáveis, três papéis, histórico com snapshots e importação
local que cria cópia. O login ainda era fictício e não havia isolamento multiusuário.

A fonte auditada tem SHA-256
b06d2d4e064fdafd8c2edae0130435175022da7c62dc2221ee881edb1ae949e7.
As fixtures contêm 600 casos e cinco inválidos; o snapshot SQLite tem 11 objetos.

O clone do OneDrive foi atualizado pelo usuário até f669ce2, com develop local
integrado e feature/render-deploy publicada. Este ambiente não conseguiu escrever
seu índice Git. O desenvolvimento foi realizado em clone isolado em
work/apolo-desenvolvimento, criado por bundle, com o histórico preservado.
Não foram alteradas ACLs nem copiados originals, data ou credenciais.

Main permanece na baseline. Develop foi atualizado por fast-forward no clone
isolado, e cada etapa começou numa feature a partir dessa integração.
O bundle entregue permite transportar os commits sem refazer mudanças à mão.

## 2. Arquitetura implementada

Core é matemática pura. Services coordena os casos de uso e exige permissões.
Repositories traduzem operações para SQLite ou API Supabase. Auth confirma a
identidade. Streamlit apresenta formulários e mensagens, sem calcular fórmulas.

PostgreSQL é o banco do Supabase. O app conversa com sua API HTTPS PostgREST;
não recebe senha de PostgreSQL nem usa conexão administrativa em produção.
O cliente HTTP pequeno usa biblioteca padrão Python, com timeout, sem redirects
e erros genéricos. Isso evitou introduzir um SDK completo para poucas operações.
A contrapartida é manter e testar esse pequeno adaptador explicitamente.

O Render executa o processo Streamlit. Não é responsável pelo banco. Seus
arquivos temporários podem desaparecer sem apagar o histórico persistido no Supabase.

## 3. Diagrama textual antes/depois

    Antes:
    navegador -> Streamlit -> serviço -> core
                                  |
                                  +-> SQLite em arquivo
    provider local -> papel fixo de teste

    Depois, modo online:
    navegador -> Streamlit no Render -> serviços -> core intacto
                     |                    |
                     | Auth/session       +-> contrato de repository
                     v                           |
                 Supabase Auth                   v
                 perfil protegido          API HTTPS + JWT individual
                                                 |
                                                 v
                                            PostgreSQL
                                          grants + RLS + RPC

    Modo dev:
    mesmo Streamlit/serviço/core -> RepositorioSQLite -> cópia local

Autenticação responde “quem é?”. Autorização responde “o que pode fazer?”.
RLS responde “quais linhas desse banco pode acessar?”. São camadas complementares.

## 4. Árvore final deste pacote

    apolo_web/
      .github/workflows/tests.yml
      .streamlit/config.toml
      .env.example / .gitignore
      app.py / config.py / iniciar.ps1 / render.yaml
      core/
        calculos.py / catalogo.py / __init__.py
      auth/
        provider.py / supabase_provider.py / roles.py / __init__.py
      services/
        apolo.py / projects.py / __init__.py
      database/
        contracts.py / repository.py / supabase_repository.py
        schema.sql / __init__.py
      integrations/
        supabase_http.py / __init__.py
      interface/
        telas.py / __init__.py
      supabase/migrations/
        202610030001_schema.sql
        202610030002_catalog.sql
        202610030003_security_rpc.sql
      supabase/verificacoes/20261003_instalacao.sql
      docs/VALIDACAO_ONLINE_MARCO_02.md
      docs/VALIDACAO_E2E_OPERADOR.md
      supabase/verificacoes/20261003_e2e.sql / 20261003_operador.sql
      tools/
        importar_banco.py / gerar_fixtures_legado.py / iniciar_online.py
        __init__.py
      tests/
        conftest.py
        test_equivalencia.py / test_banco_e_papeis.py / test_bancos_reais.py
        test_interface.py / test_contrato_persistencia.py
        test_supabase_repository.py / test_supabase_auth.py
        test_interface_online.py / test_postgres_integracao.py
        test_render_deploy.py
        fixtures/equivalencia_apolo_26.json / schema_apolo_26.json
      requirements.txt / requirements-dev.txt
      README.md / AUDITORIA.md / auditoria.json / preview.jpg
      MANUAL_TECNICO_APOLO_WEB_IMPLEMENTADO.md
      CHANGELOG_IMPLEMENTACAO.md
      originals/ / data/ / .venv/ / .env   [locais, não versionados]

Os arquivos AUDITORIA.md, auditoria.json e preview.jpg são históricos recebidos,
não evidência de validação online. Pastas auxiliares do Codex não são dependências.

## 5. Fluxo completo de uma operação

1. O navegador interage com Streamlit, que reexecuta app.py.
2. Configuracao escolhe um par coerente: local/sqlite ou supabase/supabase.
3. No modo online, Auth confirma o usuário e o perfil; um projeto próprio é escolhido.
4. A tela consulta valores por ServicoApolo.consultar().
5. Ao calcular, ServicoApolo.executar() exige CALCULAR e chama core.calculos.calcular().
6. Somente as entradas declaradas no catálogo entram no snapshot.
7. O repository envia uma única chamada apolo_save_execution.
8. PostgreSQL verifica dono, catálogo, nomes e números finitos; grava execução,
   snapshots e valores atuais na mesma transação.
9. O ID retornado identifica a gravação. A tela mostra resultado e histórico.

Se a gravação falhar, não se anuncia cálculo salvo. Se parte do snapshot for
inválida, a transação inteira deve voltar atrás. Sem atomicidade, poderia haver
execução no histórico sem todos os valores que explicam seu resultado.
As operações não têm retry automático: uma resposta de rede perdida após commit
pode deixar a execução salva; consulte o histórico antes de repetir.

## 6. Fluxo de autenticação e sessão

Antes, ProvedorLocal lia APOLO_LOCAL_ROLE e criava identidade de demonstração.
Agora auth/supabase_provider.py implementa ProvedorSupabase:

- POST /auth/v1/token, grant_type=password, envia email/senha ao Auth.
- Access token, refresh token e expiração ficam somente em st.session_state.
- Antes de expirar, o refresh token solicita uma sessão renovada.
- GET /auth/v1/user confirma a identidade no Supabase; não se confia em JWT
  apenas decodificado localmente.
- A API consulta o próprio profiles. O papel vem desse registro protegido.
- Logout pede revogação da sessão local no Auth e limpa o estado do navegador.

Senha não é persistida nem colocada na linha de comando/logs. Tokens não aparecem
no repr da sessão. O cliente é criado por sessão, sem cache global compartilhado.
Revalidar o profile em cada execução reflete mudanças de papel no próximo rerun.

Sessão é recuperada entre interações da mesma sessão Streamlit; não há cookie
persistente customizado. Recarregar/abrir nova aba ou reiniciar o servidor pode
exigir novo login. Isso é uma limitação deliberada, não um “lembrar de mim”.

Logout não elimina imediatamente um access token JWT já emitido: ele pode valer
até sua expiração. Se a revogação remota falhar, a interface avisa; o estado local
continua limpo. Recuperação de senha, cadastro público, MFA e OAuth ficaram adiados.
Usuários deste piloto são criados pelo administrador no painel Supabase.

## 7. Fluxo de autorização

auth/roles.py conserva a matriz:

| Papel | Consultar/calcular | Configurar projeto próprio | Diagnóstico próprio |
| --- | --- | --- | --- |
| OPERADOR | Sim | Não | Não |
| ADMIN | Sim | Sim | Não |
| DESENVOLVEDOR | Sim | Sim | Sim |

Os serviços chamam exigir() antes da ação. A tela só apresenta páginas pertinentes.
As RPCs também leem o papel protegido no banco para configuração/diagnóstico.
Assim, chamar a API diretamente não concede essas funções ao operador.

ADMIN não é dono de todos os dados: todos os papéis estão limitados aos seus
próprios projetos. DESENVOLVEDOR tem importação na ferramenta local existente,
mas não foi criada uma importação online nem um painel de gestão de outros usuários.
Não há endpoint para promover a si próprio.

## 8. Estrutura PostgreSQL e migrations

As migrations são arquivos SQL aplicados uma vez e em ordem no projeto dedicado:

| Migration | Conteúdo | Por que existe |
| --- | --- | --- |
| 202610030001_schema.sql | Oito tabelas, FKs, constraints, índices, RLS habilitada e grants revogados | Criar modelo online sem expor tabelas durante a instalação |
| 202610030002_catalog.sql | 23 variáveis, seis cálculos e dependências com IDs/metadados preservados | Manter a identidade do catálogo auditado |
| 202610030003_security_rpc.sql | Profiles, defaults de projeto, grants, policies e três RPCs | Isolamento e operações atômicas autorizadas |

Cada arquivo usa transação. O app não executa migrations a cada abertura.
Elas não são idempotentes nem uma conversão de banco legado; não as reaplique
sobre um banco já instalado. Registre no processo de implantação quais foram aplicadas.
Em projeto com tabelas de mesmo nome, pare e revise antes de executar.
Não houve aplicação em banco real neste ambiente.

## 9. Tabelas e relacionamentos

| Tabela | Responsabilidade e ligação |
| --- | --- |
| profiles | Um profile por auth.users.id; nome e papel protegido |
| variables | Catálogo comum de variáveis, tipos, unidades e defaults |
| calculations | Catálogo comum de cálculos e metadados da versão |
| calculation_dependencies | Cálculo -> variável, entrada/saída e ordem |
| projects | Projeto privado -> profiles proprietário |
| project_values | Valor atual de cada variável em cada projeto |
| executions | Execução -> projeto, usuário e cálculo |
| execution_values | Snapshot -> execução e variável, papel e unidade |

    auth.users -> profiles -> projects -> executions -> execution_values
                                  |          |
                                  v          v
                            project_values  calculations
                                  |              |
                                  v              v
                               variables <- calculation_dependencies

UUIDs identificam usuários/projetos/execuções. IDs estáveis do Apolo identificam
variáveis e cálculos. Double precision mantém representação de float Python;
não houve arredondamento novo na persistência. Snapshots são imutáveis para o cliente.
Valores atuais são atualizados; o histórico não depende deles para se explicar.

## 10. Políticas RLS, grants e RPCs

RLS foi escrita, mas ainda exige a execução real dos testes SQL. As políticas:

| Alvo | Regra de leitura/escrita |
| --- | --- |
| profiles | Só ler o próprio; nenhuma escrita concedida ao cliente |
| variables/calculations/dependencies | Leitura para usuário autenticado; sem escrita de cliente |
| projects | Ler os próprios; criar somente com owner_id=auth.uid() |
| project_values | Ler somente valores de projeto próprio; escrita só por RPC |
| executions | Ler se user_id=auth.uid() e projeto pertence ao usuário |
| execution_values | Ler se execução pai pertence ao usuário; escrita só por RPC |

Anon não recebe SELECT ou EXECUTE nas operações Apolo. O trigger de profiles
sempre cria OPERADOR, mesmo que metadata do cadastro peça desenvolvedor.
O trigger de projeto inicializa seus 23 valores.

apolo_save_execution valida dono e snapshot, bloqueia o projeto durante a operação
e grava tudo atomicamente. apolo_configure exige ADMIN/DESENVOLVEDOR e impede
alteração de saída. apolo_diagnostics exige DESENVOLVEDOR e só retorna contagens
do contexto próprio. Funções definer usam search_path vazio, nomes qualificados,
grants explícitos e helpers em schema privado não exposto.

Funções SECURITY DEFINER operam com privilégios do dono: por isso não basta
habilitar RLS nas tabelas; as funções também verificam auth.uid e dono/papel.
Sem isso, uma RPC poderia contornar o isolamento.
A chave service_role/sb_secret contorna proteções e nunca é usada pelo app.

A RPC não recalcula as equações SQL. Ela valida a estrutura e números e recebe
os resultados calculados pelo core. Um cliente que chame a API diretamente pode
forjar resultados nos próprios projetos. O piloto garante isolamento/autorização,
não certificação científica contra adulteração do próprio autor. Se for exigido
histórico certificado, será necessário um backend confiável de cálculo.

Referências: [RLS Supabase](https://supabase.com/docs/guides/database/postgres/row-level-security),
[profiles e triggers](https://supabase.com/docs/guides/auth/managing-user-data).

## 11. Como Streamlit usa services

app.py é a composição: configura, autentica, seleciona projeto/banco e cria serviço.
interface/telas.py apresenta cálculo, histórico, variáveis, administração e diagnóstico.
Ela chama o serviço; não faz SQL nem decide a fórmula.

Antes, chaves da interface e diagnósticos usavam repo.path. Agora repo.contexto
identifica o banco local ou usuário/projeto online. Resultados de um contexto
não são reapresentados como se fossem de outro. Diagnóstico passa pelo serviço,
em vez de ler arquivo diretamente. Sem isso, a tela dependeria de um SQLite fictício.

## 12. Como services usam repositories

database/contracts.py contém Protocol RepositorioCalculos: contexto, variaveis,
salvar_execucao, configurar, historico, detalhe e diagnostico. É um contrato
estrutural: implementações oferecem as operações, sem herança obrigatória.

ServicoApolo usa esse contrato, não um SQLite concreto. ServicoProjetos valida
nome (1 a 120 caracteres), exige permissões e delega criar/listar/selecionar.
Não foi acrescentada uma interface genérica enorme para operações inexistentes.

Um teste com repository em memória prova que o serviço calcula/salva sem arquivo
e rejeita permissões fora da interface. Sem contrato, detalhes de um banco
poderiam escapar para as regras de aplicação.

## 13. SQLite x RepositorioSupabase

| Característica | SQLite | Supabase |
| --- | --- | --- |
| Transporte | Arquivo local | HTTPS REST/RPC |
| Identidade do contexto | Caminho de banco | UUID de usuário e projeto |
| Execução | Transação SQL local | RPC PostgreSQL atômica |
| ID de execução | Inteiro | UUID |
| Valores atuais | Por banco | Por projeto |
| Isolamento | Papel local demonstrativo | JWT, grants, RLS e guardas de RPC |
| Disponibilidade | Pasta gravável | Rede e serviços externos |

O schema SQLite foi conservado para equivalência, importação e testes.
Não se obrigou o schema online a imitar um arquivo de usuário único.
O repository online adapta aliases para a interface continuar recebendo listas/dicts
sem saber se o ID é inteiro ou UUID. Falhas de sessão/rede são diferentes de erro matemático.

## 14. Variáveis de ambiente

| Nome | Uso |
| --- | --- |
| APOLO_ENV | development ou production; Render exige production |
| APOLO_AUTH_MODE | local ou supabase |
| APOLO_REPOSITORY_MODE | sqlite ou supabase, combinado com auth |
| APOLO_LOCAL_ROLE | operador/admin/desenvolvedor, só local |
| APOLO_DATA_DIR | Pasta SQLite local opcional |
| SUPABASE_URL | URL HTTPS do projeto online |
| SUPABASE_PUBLISHABLE_KEY | Publishable; anon legada aceita; secret/service_role rejeitadas |
| PORT | Porta do processo online; default 10000, intervalo 1..65535 |
| PYTHON_VERSION | Python 3.12.10 no Render |
| APOLO_TEST_POSTGRES_DSN | Conexão de PostgreSQL dedicado de testes, não produção |
| APOLO_TEST_POSTGRES_ISOLATED | Deve ser 1 para autorizar bootstrap de teste |

.env.example é documentação. O programa **não carrega .env automaticamente**.
Defina valores no terminal ou painel Render. URL não permite credenciais,
query/path/fragment. Produção recusa provider local e combinações inconsistentes.
O iniciador valida isso antes de abrir porta. Não imprimir valores em relatórios.

## 15. Secrets e proteção do Git

Senha de usuário, refresh/access token, senha PostgreSQL e chave administrativa
são credenciais. Não entram no Git nem devem ser enviadas nesta conversa.
Mesmo apagar uma credencial de um arquivo pode deixá-la no histórico Git.
Em caso de vazamento, revogue/rotacione; não basta apagar.

A publishable key é pública por desenho do Supabase, mas seus valores reais
também são configurados externamente, não no código. A proteção dos dados
vem de JWT/RLS/grants, não de esconder uma chave pública.
.gitignore exclui .env e variantes, secrets.toml, originals, data e venv.
Nenhum dado real ou secret foi necessário para escrever/testar este pacote.

## 16. Configuração Supabase — ação externa necessária

1. Crie um projeto dedicado de desenvolvimento, sem dados reais e sem tabelas Apolo
   existentes. Guarde a senha do banco fora do Git.
2. Antes de aplicar SQL, confirme CI PostgreSQL verde.
3. No SQL Editor, aplique 001, depois 002, depois 003, exatamente uma vez.
4. Confira oito tabelas, 23 variáveis, seis cálculos, RLS habilitada e funções.
5. Em Authentication, mantenha email/password disponível. Para este piloto,
   crie contas de teste pelo painel, confirmadas, sem cadastro público na interface.
6. Use pelo menos dois operadores e uma conta administrativa para validar isolamento.
   A criação de conta produz profile operador automaticamente.
7. Quando necessário, promova a conta correta usando SQL administrativo:

       update public.profiles set role='admin' where id='<UUID da conta de teste>';

   Faça o mesmo para desenvolvedor em conta de teste específica. Nunca conceda
   UPDATE de profiles ao authenticated nem use user_metadata.role como autoridade.
8. Configure a URL e publishable key no ambiente do app. Não envie senha/token.
9. Faça os testes da seção 26. Não carregue bancos legados em produção neste piloto.

Ao usar SQL Editor manualmente, mantenha registro das migrations aplicadas.
Os testes de bootstrap PostgreSQL NÃO devem ser apontados para este Supabase:
eles criam auth/users/roles e são feitos para banco descartável vazio.
Referência Auth: [endpoints oficiais](https://github.com/supabase/auth/blob/master/openapi.yaml).

## 17. Configuração Render

render.yaml prepara Web Service Python, plano free, branch feature/render-deploy,
auto-deploy off, sem disco/banco Render. Plano pago não foi contratado.
O nome apolo-web é um template: revise se já houver serviço com esse nome.

Instalação real conferida: serviço apolo-web (srv-db0o97favr4c738kgleg), Ohio,
Free; endereço https://apolo-web-z74k.onrender.com/. O formulário foi preenchido
diretamente no painel com os mesmos comandos/variáveis do template, não por
importação automática do Blueprint. Deploy f669ce2 aprovado em 1 min 2 s;
auto-deploy off, sem serviço de banco/disco Render. A tela de login foi aberta.

Build: python -m pip install -r requirements.txt
Start: python -m tools.iniciar_online
Health: /_stcore/health
Endereço: 0.0.0.0; porta: PORT do Render.

O iniciador sobrescreve address/port locais por argumentos. No Linux ele
substitui o processo por Streamlit; no Windows usa subprocess com argumentos
separados para suportar caminhos com espaços. Não usa shell nem expõe secrets.
Não foram desativadas proteções CORS/XSRF.

Health ok indica processo Streamlit funcionando, não banco/Auth funcionando.
Só o login/cálculo/histórico reais confirmam dependências externas.
Referências: [Web Services](https://render.com/docs/web-services),
[Blueprint](https://render.com/docs/blueprint-spec).

## 18. Configuração GitHub Actions

.github/workflows/tests.yml executa Python 3.12, instala requirements-dev,
confere ausência dos ativos privados e roda pytest tests -q.
Push em main/develop/feature/**, PR main/develop e execução manual disparam a CI.

Um serviço PostgreSQL 16 vazio é criado em cada job. A senha apolo_test é somente
do container descartável, não credencial real. DSN e flag isolated habilitam
os oito testes de migrations, grants, RLS, papéis, rollback e 600 snapshots.
auth.users/auth.uid são stubs de preparação; PostgreSQL, RLS e transações são reais.
Isso não testa o servidor Supabase Auth ou o gateway PostgREST real.

O job tem apenas contents: read. PostgreSQL deve estar saudável antes dos testes.
O usuário publicou pelo terminal normal; a CI remota 37156911993 foi conferida
no navegador: **688 passed, 3 skipped, 0 failed em 6,22 s** para f669ce2.
Os oito testes PostgreSQL foram executados. Os três skips são históricos.
O Git HTTPS do sandbox continua limitado por credenciais/certificados;
verificação TLS permaneceu habilitada. Isso não impediu o push pelo usuário.
Referência: [PostgreSQL em Actions](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers).

## 19. Todos os arquivos criados, relativos à baseline

| Arquivos | Conexão e necessidade |
| --- | --- |
| .github/workflows/tests.yml | Testa mudanças sem depender da máquina do autor |
| MANUAL_TECNICO_APOLO_WEB_IMPLEMENTADO.md; CHANGELOG_IMPLEMENTACAO.md | Explicação e rastreabilidade |
| tests/fixtures/equivalencia_apolo_26.json; schema_apolo_26.json | Referências auditadas portáteis |
| tools/gerar_fixtures_legado.py | Regenera referência somente a partir do legado local |
| database/contracts.py | Contrato usado pelo serviço e pelos dois backends |
| config.py | Valida modo e impede produção fictícia |
| integrations/__init__.py; supabase_http.py | Pacote e transporte HTTPS sem secrets em erros |
| database/supabase_repository.py | Traduz operações para PostgREST/RPC com JWT |
| services/projects.py | Casos de uso/autorização de projetos |
| auth/supabase_provider.py | Login, refresh, identidade/perfil e logout reais |
| supabase/migrations/202610030001_schema.sql | Modelo relacional online |
| supabase/migrations/202610030002_catalog.sql | Catálogo preservado |
| supabase/migrations/202610030003_security_rpc.sql | RLS, grants, triggers e RPCs |
| render.yaml; tools/iniciar_online.py | Deploy reproduzível e startup seguro |
| tests/test_contrato_persistencia.py | Prova desacoplamento/autorizações |
| tests/test_supabase_repository.py | Configuração, transporte e contrato REST |
| tests/test_supabase_auth.py | Sessões, perfis e falhas Auth |
| tests/test_interface_online.py | Interface online/seis cálculos sem criar SQLite |
| tests/test_postgres_integracao.py | SQL/RLS/transações reais em banco descartável |
| tests/test_render_deploy.py | Porta, produção, caminhos com espaços e template |
| docs/VALIDACAO_ONLINE_MARCO_02.md | Evidências externas observadas e passagem para teste autenticado |
| supabase/verificacoes/20261003_instalacao.sql | Auditoria repetível somente leitura da instalação, não migration |
| docs/VALIDACAO_E2E_OPERADOR.md | Fluxo real UI/Auth/banco e distinção entre SQL e acesso HTTP |
| supabase/verificacoes/20261003_e2e.sql | Compara seis snapshots reais às referências e separação dos projetos |
| supabase/verificacoes/20261003_operador.sql | Verifica autorização com claims SQL controlados e rollback; não promove perfil |

O gerador e as fixtures haviam sido criados pelo usuário antes do commit 663bd2c;
“criado” nesta tabela significa novo em Git em relação à baseline.

## 20. Todos os arquivos alterados, relativos à baseline

| Arquivo | Antes -> depois; por que; risco sem mudança |
| --- | --- |
| app.py | SQLite/fake -> composição local/online, login e projetos; sem isso não há fluxo multiusuário |
| auth/provider.py | Local sem guarda de produção -> modo local explícito; evita identidade fictícia online |
| database/repository.py | SQLite sem contrato explícito -> contexto/diagnóstico; mantém schema/transações intactos |
| services/apolo.py | Dependência implícita -> Protocol e diagnóstico autorizado; evita acoplamento/acesso lateral |
| interface/telas.py | repo.path -> contexto e diagnóstico pelo serviço; evita dependência de arquivo em produção |
| iniciar.ps1 | Fallback de Python Codex -> venv própria/sistema e local/sqlite explícitos; portabilidade |
| .gitignore | Ignorava bancos seletivos -> toda data e variantes .env; evita dados/secrets versionados |
| .env.example | Só local -> opções online/porta/testes, sem valores reais; configuração reproduzível |
| README.md | Instruções do ambiente anterior -> dois modos e evidências/limitações; evita deploy inseguro |
| requirements-dev.txt | pytest -> também psycopg[binary] 3.3.6; driver só para testes PostgreSQL reais |
| tests/test_equivalencia.py | Fonte obrigatória -> JSON + auditoria opcional; conserva cobertura e SHA/seeds |
| tests/test_banco_e_papeis.py | Legado obrigatório -> schema JSON; mantém comparação exata de 11 objetos |
| tests/test_bancos_reais.py | Bancos obrigatórios -> skip por ausência, auditoria preservada quando presentes |

requirements.txt, core/calculos.py, core/catalogo.py, database/schema.sql,
.streamlit/config.toml e fórmulas permaneceram inalterados.
iniciar.ps1 roda localhost; o iniciador online atende ao endereço de produção.

## 21. Testes existentes e novos

Os testes originais mantêm 600 equivalências, seis resultados independentes,
cinco Breguet inválidos, NaN/inf/overflow, schema, autorização, snapshots,
rollback, concorrência, importação e interface local.
As fixtures não foram recalculadas pelo novo core para “confirmar a si mesmo”.

Novos testes verificam repository sem path, RPC única, projeto/contexto, catálogo
completo, erros HTTP seguros, key administrativa rejeitada, refresh expirado,
profile errado/ausente, rede diferente de credencial inválida, logout e UI online.
AppTest atravessa formulários e serviços com API controlada, incluindo os seis
cálculos, histórico e criação de projeto. Não representa login real.

Os oito testes PostgreSQL são pulados somente quando não há DSN. Se a CI fornecer
DSN e o driver faltar, ou SQL/RLS falhar, devem falhar, não virar skip.
O bootstrap exige isolated=1 e recusa um banco que já contém profiles;
não apaga tabelas para se acomodar a um banco existente.

## 22. Resultado final observado e pendências de evidência

| Execução | Passed | Skipped | Failed | Evidência |
| --- | ---: | ---: | ---: | --- |
| 663bd2c, terminal usuário com ativos | 640 | 0 | 0 | pytest padrão informado pelo usuário |
| 663bd2c, cópia portátil usuário | 637 | 3 | 0 | pytest padrão informado pelo usuário |
| 49f602f, estabilização | 637 | 3 | 0 | Runner diagnóstico |
| 40d863c, contrato | 639 | 3 | 0 | Runner diagnóstico |
| bce8338, database/RLS | 652 | 11 | 0 | Runner diagnóstico; SQL real pulado |
| c00bdad, Auth/UI | 671 | 11 | 0 | Runner diagnóstico + AppTest |
| 2ba3979, CI/Render | 680 | 11 | 0 | Runner diagnóstico, 15,18 s |
| f669ce2, terminal usuário com ativos | 683 | 8 | 0 | pytest padrão, 16,70 s |
| f669ce2, cópia portátil usuário | 680 | 11 | 0 | pytest padrão, 22,11 s |
| f669ce2, GitHub Actions PostgreSQL 16 | 688 | 3 | 0 | CI real, 6,22 s |

O sandbox não consegue usar certos temporários criados pelo pytest/Python:
a tentativa padrão anterior produziu erros de setup. O runner auxiliar, fora
do repo, substitui apenas tmp_path por diretórios únicos com permissões herdadas
e desativa tmpdir/cache. Não alterou ACLs, testes ou bibliotecas.
Há ainda PermissionError na limpeza de TemporaryDirectory ao encerrar o processo.
O runner diagnóstico não conta como execução padrão. A execução padrão foi
posteriormente aprovada no terminal do usuário e na CI, conforme tabela acima.

Validação de fumaça: Streamlit local respondeu ok em 8517; iniciador online com
configuração de exemplo respondeu ok em 0.0.0.0:8518. Ambos foram encerrados.
O navegador confirmou migrations/auditoria no Supabase e deploy/tela de login
no Render. Depois foram aprovados login/logout, seis cálculos persistidos,
histórico, separação A/B, recusa Breguet e login negativo numa conta real.
CI, PostgreSQL real isolado e testes padrão foram confirmados; autenticação
entre duas pessoas, papéis privilegiados e refresh real ainda precisam de validação.

## 23. Como rodar localmente

Na raiz do projeto, Python 3.12:

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
    .\.venv\Scripts\python.exe -m pytest tests -q

Recrie venv se mover/clonar o projeto; ela não faz parte do pacote.
Não é preciso ativar a venv ou mudar a política global de scripts.

## 24. Como rodar em dev/local com SQLite

    $env:APOLO_ENV='development'
    $env:APOLO_AUTH_MODE='local'
    $env:APOLO_REPOSITORY_MODE='sqlite'
    $env:APOLO_LOCAL_ROLE='operador'
    .\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1

Ou iniciar.ps1 -Perfil operador/admin/desenvolvedor.
APOLO_DATA_DIR é opcional. Ausência de bancos cria banco novo com defaults.
Importação local valida antes de copiar; não migra/destrói a fonte.
O provider local não é segurança multiusuário; nunca exponha esse modo na internet.

## 25. Como rodar em produção/Supabase

Depois de configurar migrations e contas:

    $env:APOLO_ENV='production'
    $env:APOLO_AUTH_MODE='supabase'
    $env:APOLO_REPOSITORY_MODE='supabase'
    $env:SUPABASE_URL='<URL HTTPS do seu projeto>'
    $env:SUPABASE_PUBLISHABLE_KEY='<publishable key>'
    $env:PORT='10000'
    .\.venv\Scripts\python.exe -m tools.iniciar_online

Para ensaio apenas no seu computador, use as mesmas quatro opções online,
APOLO_ENV=development e Streamlit diretamente com address 127.0.0.1.
No Render, nunca use APOLO_ENV=development. Tokens/senhas são digitados no login,
não nesses exemplos. O modo online não cria nem consulta SQLite local.

## 26. Deploy e validação ponta a ponta — checklist obrigatório

Primeiro importe o bundle no clone original usando o roteiro entregue. Ele cria
um ponto de retorno e transporta branches sem sobrescrever originals/data.
Rode pytest padrão do novo marco; publique feature/render-deploy sem force.
Abra Actions no GitHub e confirme os testes PostgreSQL, não apenas testes mock.

Depois configure Supabase conforme seção 16. No Render, conecte o repositório
privado e escolha a feature validada/Blueprint. Configure URL e publishable key
no painel, sem colar secrets em arquivos. Faça deploy manual apenas após CI verde.
Confira startup e health; abra o app HTTPS e execute:

| Verificação real | Resultado esperado | Estado neste pacote |
| --- | --- | --- |
| Login correto/incorreto e logout | Identidade real; recusa segura; estado limpo | Aprovado no Render/Supabase |
| Expiração/refresh e conta sem profile | Renovação ou novo login; falha fechada | Pendente |
| Operador, admin e desenvolvedor | Matriz de papel na UI, serviço e banco | Pendente |
| Criar/selecionar dois projetos | Defaults e históricos separados | Aprovado A/B do mesmo proprietário |
| Os seis cálculos e histórico | Referências e snapshots equivalentes | Aprovado real: seis execuções, 30 valores |
| Dois usuários tentam acesso cruzado | SELECT vazio e RPC negada | PostgreSQL CI aprovado; PostgREST real pendente |
| Alterar papel/defaults direto pela API | Negado ao cliente | PostgreSQL CI aprovado; API real pendente |
| Reiniciar serviço | Dados conservados; novo login se necessário | Pendente |
| Novo deploy | Mesmo histórico no Supabase, sem SQLite Render | Pendente |
| CI com 600 snapshots | Persistência exata em PostgreSQL | Aprovado: 688 passed, 3 skipped |
| Instalação/health/tela de login | Produção sem SQLite; serviço disponível | Aprovado no Render |

Registre data, commit, evidência e resultado de cada item, sem tokens/senhas.
Só então integre a versão validada em develop remoto e, após aprovação, main.
Nenhum merge em main ou deploy externo foi feito por este pacote.

## 27. Como diagnosticar erros

- Configuração recusada: confira par auth/repository e production no Render.
- Não entra: confirme conta/email/password e confirmação no Supabase; não exponha erro bruto.
- Perfil ausente: confira migration 003, trigger e registro do próprio usuário.
- Projeto/catálogo incompleto: confira 23 defaults, seed e ordem das migrations.
- HTTP 401: sessão expirada; novo login/refresh. HTTP 403: escopo/papel/grants.
- Erro REST/RPC genérico: verifique migrations, cache PostgREST e logs no painel,
  sem copiar cabeçalhos Authorization.
- Health verde e cálculo falha: health só mede Streamlit; teste dependência externa.
- SQLite: pasta gravável, integridade/schema; não “corrigir” apagando dados reais.
- Git HTTPS deste ambiente: publicar pelo terminal normal autenticado; não desabilitar TLS.
- Temporários de teste: usar terminal normal para pytest padrão; não remover cobertura
  nem alterar fórmula para resolver PermissionError.

Erro de rede não causa retry/gravação automática. Verifique histórico antes de repetir.
Diagnóstico da interface só traz informações do contexto autorizado, não secrets.

## 28. Limitações e riscos remanescentes

SQL/RLS preparados mas ainda não executados em PostgreSQL real.
CI/deploy não publicados; Supabase Auth/PostgREST e reinícios ainda não validados.
Sessão não persistente entre novas conexões; logout segue validade natural do JWT.
Sem recuperação de senha/cadastro público, compartilhamento, gestão global de usuários,
importação SQLite->online, paginação além das últimas 200 execuções e soft-delete.
Uma chamada direta autorizada pode forjar resultados próprios, conforme seção 10.
Sem chave de idempotência, retry manual após resposta perdida pode duplicar execução.

Runtime pinado em Streamlit 1.64.0; dependências transitivas não têm lock completo.
O plano free do Render é apenas piloto; verifique limites/pausas no painel antes
de usar como serviço operacional. Backup/restore do Supabase deve ser planejado
antes de incluir dados reais. Não há benchmark/carga ou auditoria externa de segurança.

## 29. Decisões adiadas e preservação de escopo

Não modelar empresas/equipes agora. Admin/developer não ganham acesso a terceiros.
Não portar regras matemáticas para SQL ou Streamlit. Não automatizar migrations
com credencial administrativa no processo web. Não contratar serviços pagos.
Não regenerar fixtures nem migrar bancos originais sem necessidade.
Não esconder falhas reais de CI com skips nem enfraquecer TLS/CORS/XSRF.

A parte externa requer somente conexão autenticada ao GitHub e configuração do
projeto Supabase/serviço Render. Os valores reais permanecem no seu ambiente.

## 30. Caminho sugerido para Apolo 3 e aprendizado

Primeiro concluir o checklist real e registrar resultados. Depois avaliar
idempotência, paginação, autenticação persistente/recuperação de senha, backups,
compartilhamento e backend de cálculo certificado. Novas fórmulas exigem referências
independentes, testes explícitos e versionamento dos metadados/migrations.

Para seu próximo programa simples, replique o percurso com um cadastro:
tela -> serviço com permissão -> contrato -> repository -> tabela com dono/RLS.
Só depois acrescente histórico e papéis. Não copie engenharia/complexidade
que não existe no problema. Essa separação permite testar Python sem internet
e substituir o banco sem reescrever a interface ou regra.

## 31. Glossário das tecnologias

| Termo | Significado no projeto |
| --- | --- |
| Streamlit/rerun | Interface Python; interações reexecutam o script |
| Session state | Memória individual da conexão Streamlit |
| Core | Fórmulas e catálogo independentes |
| Serviço | Caso de uso com autorização |
| Protocol | Contrato estrutural de operações |
| Repository | Tradutor entre caso de uso e persistência |
| SQLite | Banco em arquivo para desenvolvimento/legado |
| PostgreSQL | Banco relacional online |
| Supabase | PostgreSQL, Auth e API gerenciados |
| PostgREST | API HTTP de tabelas/funções PostgreSQL |
| Auth/JWT | Confirma identidade e apresenta token assinado |
| Access/refresh token | Acesso temporário/renovação de sessão |
| Papel | Conjunto de operações permitido |
| RLS | Política que restringe linhas acessíveis |
| Grant | Permissão SQL de operação sobre objeto |
| RPC | Chamada de função de banco pela API |
| SECURITY DEFINER | Função executada com privilégios do dono |
| Transação/rollback | Tudo gravado junto ou nada gravado |
| Snapshot | Registro dos valores usados em execução |
| Migration | Alteração SQL versionada e aplicada em ordem |
| Fixture/SHA-256 | Referência de teste/identificador do conteúdo auditado |
| CI/Actions | Execução automatizada de testes no GitHub |
| Render/Blueprint | Hospedagem do processo/arquivo de configuração |
| Secret/TLS | Credencial/conexão criptografada verificada |
| Feature/develop/main | Mudança isolada/integração/versão estável |
| Commit/bundle | Ponto no histórico/pacote transportável de commits |
| Mock/AppTest | Resposta controlada/teste programático da interface |
| Teste de fumaça | Verificação básica de startup, não validação integral |

Consulte CHANGELOG_IMPLEMENTACAO.md para a relação etapa/commit e o relatório
entregue para o estado de bloqueio externo. Este manual deve receber as evidências
reais na próxima execução; seu título não significa deploy concluído.
