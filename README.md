# Apolo Web — primeira versão local

Migração do Apolo 2.6.0 para Streamlit, com as seis fórmulas e o schema SQLite v2 preservados. O código da interface Colab não é executado pela aplicação web.

## Experimentar agora

A aplicação iniciada nesta sessão está em **http://127.0.0.1:8501**. Esse endereço funciona apenas neste computador, enquanto o processo estiver rodando.

1. Selecione a equação em **Novo cálculo**.
2. Preencha as entradas nas unidades indicadas e clique em **Calcular e salvar**.
3. Consulte **Histórico** para ver entradas e resultados de cada execução.
4. Em **Banco de variáveis**, consulte os valores atuais e, opcionalmente, um gráfico por unidade.

Exemplo de sustentação: densidade 1,225 kg/m³, velocidade 50 m/s, área 10 m² e Cl 0,8 produzem **12.250 N**. O teste visual já salvou esse exemplo como execução 2 na cópia do banco principal. A execução 1 importada continua disponível.

O banco padrão é `data/Banco_de_Variaveis_Calculo_1_web.db`. A outra opção é `data/123_web.db`. São bancos independentes: selecionar um não mescla nem altera o outro. Os arquivos em `originals/` e os arquivos recebidos em Downloads não são usados para gravação.

## Reiniciar neste computador

Abra um terminal PowerShell **na pasta deste projeto** e execute:

```powershell
.\iniciar.ps1 -Perfil operador
```

O iniciador encontra o ambiente Python preparado nesta sessão. Para testar outros papéis, encerre o processo anterior com Ctrl+C e execute um destes comandos:

```powershell
.\iniciar.ps1 -Perfil admin
.\iniciar.ps1 -Perfil desenvolvedor
```

Não é necessário mudar a política global do PowerShell. Se a execução de scripts estiver bloqueada, use a alternativa direta abaixo com o Python preparado:

```powershell
$env:APOLO_AUTH_MODE = 'local'
$env:APOLO_LOCAL_ROLE = 'operador'
& '..\..\work\venv\Scripts\python.exe' -m streamlit run app.py --server.address 127.0.0.1
```

## Instalar em outra pasta ou computador

Use Python 3.12 (versão utilizada na verificação). Dentro da pasta do projeto:

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
.\iniciar.ps1 -Perfil operador
```

Se a pasta for movida, crie o ambiente `.venv` nela; não copie o ambiente virtual desta sessão. O arquivo `.env.example` documenta as opções, mas a aplicação não carrega `.env` automaticamente. Configure variáveis de ambiente no terminal ou, futuramente, na hospedagem. O iniciador força o modo local.

## Estrutura e locais de edição

```text
app.py                    inicialização e navegação
core/
  calculos.py             fórmulas puras e validações numéricas
  catalogo.py             catálogo preservado do notebook
interface/telas.py        formulários, histórico, consulta e administração
services/apolo.py         operações com verificação de permissões
database/
  repository.py           acesso SQLite e transações
  schema.sql              estrutura original do banco, sem novas tabelas
auth/
  roles.py                matriz de permissões
  provider.py             identidade de teste e contrato do provedor futuro
tools/importar_banco.py   auditoria/importação segura para uma cópia nova
tests/                    equivalência, banco, papéis e interface
originals/                fontes e bancos recebidos preservados
data/                     cópias de trabalho graváveis
```

Editar o código continua sendo uma tarefa no editor de desenvolvimento, não no painel web. O painel de admin altera valores de entrada/configuração; não permite escrever Python ou mudar fórmulas. A restrição de quem pode editar o código dependerá das permissões do futuro repositório privado e da hospedagem.

## Papéis preparados — ainda sem login

| Papel | Calcular e consultar | Configurar entradas | Diagnósticos/importação local |
| --- | --- | --- | --- |
| operador | Sim | Não | Não |
| admin | Sim | Sim | Não |
| desenvolvedor | Sim | Sim | Sim |

As operações passam por verificações de permissão no serviço, além de ocultar páginas indisponíveis. O papel é configurado **no servidor**, não escolhido pelo visitante.

**Este modo é uma demonstração local, não autenticação.** Todas as sessões deste processo recebem o mesmo perfil de teste. Não há cadastro, senha, verificação de token ou separação do histórico por usuário. Não publique esta versão na internet nem exponha a porta na rede. Modos de autenticação não implementados são recusados; definir `APOLO_AUTH_MODE=supabase` não ativa uma integração fictícia.

## Importar outro banco, sem modificar a origem

Os dois bancos fornecidos já foram importados. Para verificar um arquivo adicional:

```powershell
python -m tools.importar_banco 'C:\caminho\Banco.db' --audit-only
```

Para criar uma cópia nova, use o Python com as dependências e um perfil desenvolvedor configurado no terminal:

```powershell
$env:APOLO_AUTH_MODE = 'local'
$env:APOLO_LOCAL_ROLE = 'desenvolvedor'
python -m tools.importar_banco 'C:\caminho\Banco.db' --nome Novo_Projeto.db
```

O importador valida schema, catálogo, integridade e relações, usa uma cópia consistente do SQLite e verifica que o conteúdo da origem não mudou. Recusa sobrescrever arquivos e rejeita nomes com caminhos. Bancos antigos ou incompatíveis são recusados, não convertidos silenciosamente.

## Verificação

Resultado final: **639 testes passaram**, sem falhas, em Python 3.12 e Streamlit 1.64.0. O relatório está em `test-results.xml`; os detalhes da auditoria estão em `AUDITORIA.md` e `auditoria.json`.

Para rodar em um ambiente Python instalado normalmente:

```powershell
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-dev.txt
& '.\.venv\Scripts\python.exe' -m pytest tests -q
```

Os testes criam bancos temporários; não gravam nos bancos em `originals/`. A suíte contém 600 comparações numéricas com os callbacks originais, seis exemplos de referência, comparação do schema, reexecução dos oito históricos recebidos e testes de interface/permissões/transações.

O valor de Breguet permanece em metros, com velocidade em m/s e consumo específico em s⁻¹. Não foi acrescentada conversão automática. Os modelos físicos originais não foram ampliados; esta migração não constitui validação para decisões de segurança aeronáutica.

## Próximas etapas para uma versão online

1. Integrar Supabase Auth ao contrato de identidade: validar a sessão/token no servidor e obter o papel de uma fonte protegida. Cadastro deve sempre criar operador; o usuário não pode promover a si próprio.
2. Definir o acesso ao histórico: compartilhado, por usuário ou por organização. O schema preservado não possui identificação de proprietário. Para isolamento, será necessária uma migração adicional, versionada, ou tabelas auxiliares de propriedade.
3. Planejar PostgreSQL/Supabase separadamente: converter tipos, sequências e relações, comparar dados e resultados e configurar políticas de acesso. Preservar SQLite agora não significa que o banco já esteja migrado para Supabase.
4. Configurar repositório privado, revisão de alterações e segredos da hospedagem. Os arquivos `.db`, `originals/`, ambientes virtuais e `.env` estão ignorados pelo Git.
5. Testar login/logout, expiração de sessão, tentativa de promoção, isolamento, backup e implantação antes de liberar operadores reais.

Nada foi publicado; não houve criação de usuários nem alteração de recursos no Supabase, GitHub ou Drive.

Referências de implementação: documentação oficial de [formulários Streamlit](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form), [estado de sessão](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state) e [testes de aplicações](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).
