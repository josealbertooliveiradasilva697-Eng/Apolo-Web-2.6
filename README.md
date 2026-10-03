# Apolo Web

Seis cálculos do Apolo 2.6.0 em Streamlit, com serviços, autorização e SQLite.
A versão online Supabase/Render está em desenvolvimento. O manual distingue
o que foi implementado e o que falta validar.

## Executar localmente

Use Python 3.12. Na raiz:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:APOLO_AUTH_MODE = 'local'
$env:APOLO_LOCAL_ROLE = 'operador'
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Ou use iniciar.ps1 -Perfil operador, se a política local permitir scripts.
O iniciador usa apenas a venv do projeto ou Python do sistema.
Papéis de teste: operador, admin e desenvolvedor. Recrie a venv se mover o projeto.

O app cria um banco novo em data quando não há arquivos de trabalho.
APOLO_DATA_DIR permite outra pasta gravável. Selecionar bancos não mescla históricos.
O provider local não é login: todas as sessões do processo recebem o papel
configurado. Use somente no desenvolvimento local.

## Testar

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

A suíte não exige originals/data: preserva 600 comparações exatas em JSON,
seis referências independentes, cinco inválidos de Breguet, NaN/inf/overflow,
schema, snapshots, permissões, transações e interface.
Auditorias históricas são opcionais quando os ativos não existem.

Marco 663bd2c: execução padrão confirmada pelo usuário com **640 passed** e
**637 passed, 3 skipped** sem originals/data. CI remota ainda pendente.
Não é necessário regenerar fixtures para testar. Para nova auditoria local,
execute python -m tools.gerar_fixtures_legado com a fonte presente e revise
as diferenças antes de versionar.

## Organização

- core: fórmulas/catalogo independentes de interface e infraestrutura.
- services: casos de uso e autorização.
- database: persistência/transações.
- auth: identidade/permissões.
- interface: formulários, histórico e configuração.
- tools: auditoria/importação; tests: referências/regressão.

OPERADOR consulta/calcula; ADMIN também configura; DESENVOLVEDOR também
diagnostica/importa. As permissões são verificadas no serviço.

## Importação local

```powershell
.\.venv\Scripts\python.exe -m tools.importar_banco 'C:\caminho\Banco.db' --audit-only
$env:APOLO_AUTH_MODE = 'local'
$env:APOLO_LOCAL_ROLE = 'desenvolvedor'
.\.venv\Scripts\python.exe -m tools.importar_banco 'C:\caminho\Banco.db' --nome Projeto.db
```

Importação valida schema/catálogo/integridade e cria cópia nova, preservando
a origem. originals, data, venv, .env e secrets ficam fora do Git.
.env.example documenta opções; .env não é carregado automaticamente.

## Documentação

MANUAL_TECNICO_APOLO_WEB_IMPLEMENTADO.md explica arquitetura e mudanças.
CHANGELOG_IMPLEMENTACAO.md registra evidências e commits.
AUDITORIA.md e auditoria.json são registros históricos da migração inicial.

Modelos físicos e unidades foram preservados: Breguet retorna metros e usa
consumo específico em s⁻¹. Esta migração não amplia os modelos científicos.
