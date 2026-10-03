# Manual técnico do Apolo Web — documento em evolução

Atualizado em 03/10/2026. Marco: testes portáteis e preparação de CI.

Este documento distingue o código verificado do trabalho planejado.
A migração online ainda não está implementada; não há Supabase, RLS ou deploy
concluídos neste marco. A arquitetura final será documentada quando existir.

## 1. Estado inicial recebido

Clone: `C:\Users\User\OneDrive\Documentos\Work\Projeto Apolo\Apolo_Web_Local\apolo_web`.
Baseline: `a4cd61af479430c471c2140d1d5867a511ed606b`.
Branch: `feature/ci-portable-tests`; main/develop permanecem na baseline.
Remoto configurado: repositório privado Apolo-Web-2.6. Nenhum push neste marco.

Já existiam seis fórmulas, 23 variáveis, Streamlit, serviços com autorização,
SQLite e importação para cópia. Foram recebidos como alterações pendentes:
test_equivalencia.py, duas fixtures e tools/gerar_fixtures_legado.py.
Essas alterações preexistentes foram preservadas.

Fonte auditada: Apolo_2_6_exportado.py, SHA-256
`b06d2d4e064fdafd8c2edae0130435175022da7c62dc2221ee881edb1ae949e7`.
São 600 casos numéricos, cinco inválidos de Breguet e 11 objetos de schema.

## 2. Arquitetura atual e final pretendida

Hoje core calcula, services coordena operações/permissões, database persiste,
auth fornece a identidade e interface apresenta os dados. A troca de interface
não exige alterar uma fórmula. A versão final acrescentará Auth real,
projetos e repository Supabase com RLS. Essas partes ainda não existem.

## 3. Diagrama antes/depois

```text
Atual:
Navegador -> app.py/Streamlit -> interface -> ServicoApolo
                                            |-> exigir/permissões
                                            |-> core/calculos
                                            |-> RepositorioSQLite
ProvedorLocal -----------------------------> identidade de teste

Destino planejado:
Navegador -> Streamlit no Render -> services -> contrato de repository
                                    |-> core matemático
                                    |-> autorização na aplicação
                                    |-> Supabase Auth/perfil protegido
                                    |-> Supabase API + JWT individual
                                        -> PostgreSQL + RLS
```

## 4. Árvore neste marco

```text
apolo_web/
  .github/workflows/tests.yml       preparado; CI remota pendente
  .streamlit/config.toml            configuração local
  .env.example / .gitignore
  app.py / iniciar.ps1
  core/calculos.py / catalogo.py
  services/apolo.py
  database/repository.py / schema.sql
  auth/provider.py / roles.py
  interface/telas.py
  tools/importar_banco.py / gerar_fixtures_legado.py
  tests/conftest.py
  tests/test_equivalencia.py
  tests/test_banco_e_papeis.py
  tests/test_bancos_reais.py
  tests/test_interface.py
  tests/fixtures/equivalencia_apolo_26.json
  tests/fixtures/schema_apolo_26.json
  requirements.txt / requirements-dev.txt
  README.md / AUDITORIA.md / auditoria.json
  MANUAL_TECNICO_APOLO_WEB_IMPLEMENTADO.md
  CHANGELOG_IMPLEMENTACAO.md
  originals/ / data/ / .venv/        locais, ignorados
```

Árvore resumida atual; não representa uma migração online concluída.

## 5. Fluxo completo de um cálculo

app.py identifica o papel e abre uma cópia SQLite. A tela consulta variáveis
pelo serviço e envia as entradas a executar(). O serviço exige CALCULAR,
valida o identificador e chama o core. Ele canonicaliza as entradas declaradas
no catálogo e solicita a gravação. O repository usa uma transação para registrar
a execução, seus snapshots e valores atuais. A tela mostra o resultado/JSON.
O snapshot preserva o valor usado mesmo se uma configuração posterior mudar.
Sem isso, o histórico não explicaria como um resultado foi produzido.

## 6. Fluxo de autenticação

ProvedorLocal lê APOLO_LOCAL_ROLE e retorna local-teste. Não valida senha/token;
todas as sessões recebem o mesmo perfil do processo.
Supabase Auth deverá validar usuário no servidor, renovar tokens, encerrar sessão
e tratar expiração. Papel deverá vir de profile protegido, nunca de um formulário
ou metadado de cadastro alterável pelo próprio usuário. Ainda não implementado.

## 7. Fluxo de autorização

auth/roles.py define a matriz: OPERADOR consulta/calcula; ADMIN também configura;
DESENVOLVEDOR também diagnostica/importa. exigir() lança PermissionError para
ação negada. services aplica essa verificação antes da operação.
A interface oculta páginas, mas chamar o serviço diretamente continua sujeito às
regras. Sem autorização no serviço, seria possível contornar a proteção visual.

## 8. Estrutura PostgreSQL

Ainda não criada. A etapa 4 deverá versionar migrations SQL e separar aplicação
do schema da execução normal do programa. Não converter/destruir bancos originais.
A equivalência continuará sendo verificada independentemente da persistência.

## 9. Tabelas e relacionamentos

SQLite atual: metadata, variaveis, calculos, dependencias_calculo, execucoes,
execucao_valores, variaveis_legado. Quatro índices completam os 11 objetos auditados.
Uma execução referencia um cálculo e os valores referenciam execução/variável.
Destino planejado: profiles -> usuário Auth; projects -> proprietário;
executions -> projeto, usuário e cálculo; execution_values -> execução/variável.
Configurações e valores atuais também precisarão de escopo de projeto.

## 10. Políticas RLS

Ainda não implementadas. RLS limita linhas acessíveis no banco, além das regras
da aplicação. Projetos/execuções deverão respeitar o proprietário/escopo; configurações
deverão respeitar papel; usuários não poderão promover a si próprios.
O acesso normal deve usar JWT individual; chave administrativa que contorna RLS
não deve ser o meio normal de acesso. Validação futura exigirá dois usuários,
leituras cruzadas negadas e tentativas de escrita/promoção negadas.

## 11. Como Streamlit usa services

interface/telas.py chama consultar, executar, historico, detalhe e configurar.
Recebe listas/dicionários para formulários, tabelas e mensagens. Os testes AppTest
exercitam esse fluxo. A interface ainda usa repo.path em chaves e diagnósticos;
na etapa online isso deverá ser uma identidade de contexto, não um arquivo fictício.

## 12. Como services usam repositories

ServicoApolo recebe repo no construtor e delega persistência. A injeção permite
troca, mas o contrato ainda é implícito. A etapa 3 deverá explicitar apenas
variaveis, salvar_execucao, configurar, historico e detalhe, acrescentando
operações de projeto quando efetivamente usadas.

## 13. SQLite x SupabaseRepository

SQLite usa arquivo local/transações diretas. O futuro repository Supabase enviará
operações autenticadas ao PostgreSQL pela rede, tratando indisponibilidade,
acesso negado e consistência. Gravação de execução/valores precisará ser atômica.
A interface deverá mostrar o mesmo conteúdo sem depender de caminho de arquivo.

## 14. Variáveis de ambiente

Atuais: APOLO_AUTH_MODE=local, APOLO_LOCAL_ROLE e APOLO_DATA_DIR.
.env.example documenta exemplos; o app não carrega .env automaticamente.
Ambiente verificado: Python 3.12.10, Streamlit 1.64.0, pytest 9.1.1.
Nomes/validação das opções de produção serão documentados ao implementar a integração.

## 15. Secrets

Credenciais permitem acesso a contas/dados. Uma credencial no histórico pode
continuar recuperável depois de apagar o arquivo. .env, .streamlit/secrets.toml,
originals e bancos locais estão ignorados. Não foram lidas/incluídas credenciais
reais neste marco. Antes de cada commit, revisar explicitamente os arquivos staged.

## 16. Configuração Supabase

Pendente. Será necessário projeto de desenvolvimento, schema com RLS,
configuração de Auth e usuários de teste. A ação externa será solicitada quando
código/migrations/roteiro estiverem prontos. Nenhum recurso Supabase foi alterado.

## 17. Configuração Render

Pendente. Streamlit deverá usar 0.0.0.0 e a porta do serviço, com dados no Supabase.
A configuração atual usa 127.0.0.1 para execução local; não é um deploy pronto.
Nenhum recurso Render foi criado ou alterado.

## 18. Configuração GitHub Actions

.github/workflows/tests.yml usa Python 3.12, instala requirements-dev, verifica
ausência de originals/bancos reais e executa python -m pytest tests -q.
Dispara em push de main, develop e feature/**, PR para main/develop ou manualmente.
Usa permissão contents: read.
Referência: [documentação oficial do GitHub](https://docs.github.com/en/actions/tutorials/build-and-test-code/python).
Workflow preparado, ainda não enviado/executado. Não há evidência de CI verde.
Sem CI, a integração depende de cada pessoa lembrar de rodar os testes.

## 19. Arquivos criados

Nesta continuação: workflow, manual e changelog.
Fixtures e gerador foram recebidos não versionados.
Fora do repo: runner diagnóstico, cópia portátil e roteiro PowerShell para
testes/commit manual. Auxiliares não são dependências do aplicativo ou da CI.

## 20. Arquivos alterados: antes, depois e motivo

| Arquivo | Antes | Depois e motivo |
| --- | --- | --- |
| tests/test_equivalencia.py | Migração JSON iniciada pelo usuário | Protege 600 pares cálculo/seed, cinco inválidos e SHA; mantém AST e verifica SHA local. Evita referência truncada/duplicada. |
| tests/test_banco_e_papeis.py | Executava fonte legada obrigatoriamente | Compara SQLite novo com JSON auditado; verifica 11 objetos/SHA. Permite checkout sem originals. |
| tests/test_bancos_reais.py | Exigia bancos históricos sempre | Skip por arquivo ausente; auditorias continuam completas quando presentes. |
| README.md | Descrevia suíte anterior | Explica fixtures e resultados diagnósticos sem declarar CI concluída. |

Fórmulas, catálogo, schema SQLite e comportamento do app não foram alterados.

## 21. Testes existentes e verificações reforçadas

Preservados: 600 comparações exatas, seis referências independentes, cinco
inválidos de Breguet, quatro entradas NaN/inf/overflow, schema, snapshots,
rollback, importação, concorrência, permissões e sete testes de interface.
Reforçado o teste de cardinalidade recebido para verificar exatamente 100 seeds
por cálculo, cinco inválidos e SHA fixo. O schema verifica 11 objetos e SHA.
A auditoria local verifica SHA da fonte e equivalência AST com notebook.
O core novo não foi usado para gerar as saídas esperadas.

## 22. Resultados deste marco

| Ambiente | Passed | Skipped | Failed | Observação |
| --- | ---: | ---: | ---: | --- |
| Clone real, runner diagnóstico | 640 | 0 | 0 | Mesmos testes; tmp_path com ACL herdada. |
| Cópia sem originals/data, runner diagnóstico | 637 | 3 | 0 | Duas auditorias de bancos e uma de notebook puladas. |
| pytest padrão no sandbox, tentativa inicial | 620 | 0 | 0 | 20 erros de setup por PermissionError; não é sucesso completo. |
| pytest padrão fora do sandbox | — | — | — | Pendente. |
| GitHub Actions | — | — | — | Pendente. |

Plugin diagnóstico substitui apenas tmp_path por pastas únicas com ACL herdada,
desabilitando tmpdir/cache. Não altera ACL, código dos testes ou bibliotecas.
Também há erro de limpeza de TemporaryDirectory na saída do processo do sandbox,
sem falhas nos testes. Resultado diagnóstico não substitui confirmação padrão/remota.

## 23. Como rodar localmente

Na raiz, com Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:APOLO_AUTH_MODE = 'local'
$env:APOLO_LOCAL_ROLE = 'operador'
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
.\.venv\Scripts\python.exe -m pytest tests -q
```

Não é necessário ativar a venv ou mudar a política global de scripts.

## 24. Modo dev/local com SQLite

Escolha papel de teste no ambiente e pasta gravável em APOLO_DATA_DIR.
O app cria banco novo se não houver bancos de trabalho.
Para legado, use o importador: valida schema e cria uma cópia nova; não grava
em originals. Permissões locais são para demonstração, sem isolamento de usuários.

## 25. Modo produção/Supabase

Ainda indisponível. O provider recusa modo diferente de local, evitando
autenticação fictícia. Instruções completas dependem das etapas 3 a 7.
Não publicar esta versão como aplicação multiusuário.

## 26. Como realizar deploy

Após a migração: aplicar migrations em projeto de teste, configurar Auth,
executar testes de RLS, configurar Render e validar fluxo real antes de liberar.
Build/start/secrets e passos exatos serão incluídos quando implementados.

## 27. Diagnóstico e bloqueio atual

Git retorna Unable to create .git/index.lock: Permission denied mesmo após
permissão de escrita concedida. Clones independentes falharam na criação de
signal pipe do processo sh. Nenhuma ACL/metadata foi alterada por outra via.
Isso impede os commits/branches exigidos antes da próxima mudança estrutural.
A ação mínima é executar o roteiro entregue no terminal normal.
Ele valida os testes e registra só os arquivos deste marco, sem merge/push.

Erros de cálculo devem ser separados de falhas de infraestrutura.
Para SQLite, verificar schema, integridade e pasta gravável.
Um erro de diretório temporário não justifica excluir teste ou mudar uma fórmula.

## 28. Limitações conhecidas

Sem Auth real, isolamento, PostgreSQL, RLS ou deploy. Dependência de repo.path
na tela e configuração local do iniciador ainda exigem revisão.
CI remota e pytest padrão pendentes. Interface verificada por AppTest;
nenhuma validação manual por navegador neste marco.

## 29. Decisões adiadas

Empresas/equipes não entram agora. Compartilhamento, recuperação de senha e
privilégios administrativos concretos serão definidos nas etapas correspondentes.
Papéis locais não devem virar acesso irrestrito a todos os usuários online.

## 30. Próximos passos e Apolo 3

Registrar o marco/testes padrão; integrar em develop; estabilizar ambiente;
extrair contrato; implementar schema/repository; Auth; RLS; projetos/UI;
confirmar CI; preparar Render; validar cálculo, histórico, isolamento,
sessão, reinício e novo deploy.
Apolo 3 poderá acrescentar compartilhamento e modelos físicos com novas
referências independentes/migrations. Para um projeto didático menor,
reutilize interface -> serviço -> repository com um caso simples por usuário.

## 31. Glossário

| Termo | Função |
| --- | --- |
| Streamlit | Interface Python reexecutada nas interações. |
| Core | Fórmulas/validações independentes de infraestrutura. |
| Serviço | Caso de uso e autorização. |
| Repository | Encapsula persistência. |
| SQLite | Banco em arquivo local. |
| PostgreSQL | Banco relacional planejado para produção. |
| Supabase | PostgreSQL, Auth e API planejados. |
| Auth | Identifica quem é o usuário. |
| Autorização | Decide operações permitidas. |
| RLS | Restringe linhas acessíveis no banco. |
| JWT | Token verificável de identidade/sessão. |
| Migration | Evolução versionada do schema. |
| Fixture | Referência ou preparação de teste. |
| Snapshot | Valores imutáveis de uma execução. |
| SHA-256 | Identificador criptográfico de conteúdo. |
| CI | Testes automatizados de alterações. |
| Render | Hospedagem planejada do app. |
| Secret | Credencial fora do Git. |
| Branch | Linha de desenvolvimento. |
| Commit | Ponto registrado no histórico. |
| ACL | Permissões do sistema de arquivos. |
