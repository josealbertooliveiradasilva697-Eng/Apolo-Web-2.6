# Correção do segundo envio de configuração

## Problema observado

Em produção f669ce2, ADMIN salvou um texto no projeto E2E A. No segundo envio,
a tela indicou sucesso, mas o Supabase permaneceu com o primeiro texto. A consulta
independente impediu que a mensagem de sucesso fosse tomada como prova de gravação.
O estado do projeto foi restaurado pela interface após sair/voltar à página;
o perfil temporariamente elevado voltou a OPERADOR antes de preparar a correção.

## Causa e mudança

`interface/telas.py`, função administracao, fornecia o valor atual do repository
como default de st.text_input/st.number_input, sem uma key explícita.
Depois da primeira gravação, esse default mudava no próximo rerun. Sem uma
identidade estável, Streamlit recriava o campo no segundo envio e podia substituir
a entrada enviada pelo default anterior. O serviço recebia esse valor e salvava
corretamente o conteúdo errado: não era falha de SQL, RLS, serviço ou equação.

Foi acrescentada uma chave estável por contexto e id_variavel aos dois campos.
O contexto inclui identidade/projeto no Supabase ou caminho do SQLite, evitando
reutilizar uma edição de um projeto em outro. Nenhuma regra de autorização ou
matemática foi movida para Streamlit. Sem a chave, o erro pode reaparecer sempre
que uma configuração recém-salva altera o default do formulário.

Referência primária: [identidade e ciclo de vida dos widgets Streamlit](https://docs.streamlit.io/develop/concepts/architecture/widget-behavior).
A versão permanece fixada em 1.64.0; nenhuma dependência foi atualizada.

## Testes e resultado

- tests/test_interface.py: quatro cenários ADMIN/DESENVOLVEDOR x texto/número.
  Cada um envia dois valores e lê o SQLite para conferir ambos. Antes da correção:
  4 failed, 691 deselected, 4,89 s; todos falharam no segundo valor.
- tests/test_interface_online.py: mais quatro cenários com API controlada. Conferem
  os dois valores na RPC e o project_id correto, não apenas a mensagem da tela.
- Depois: oito regressões aprovadas, 691 deselected, 6,05 s.
- Suíte completa portátil: **688 passed, 11 skipped, 0 failed**, 18,93 s.
  Runner diagnóstico externo apenas por limitações de temporários do sandbox;
  não equivale a pytest padrão/CI. Ao encerrar, persiste um PermissionError de
  limpeza de TemporaryDirectory, separado do resultado da suíte.

As 600 equivalências, seis referências independentes e demais proteções foram
mantidas. Três skips são auditorias locais ausentes e oito exigem PostgreSQL
descartável/DSN. Não executar o bootstrap desses testes no Supabase de produção.

## Git e publicação

Evidências de papéis/isolamento: d220aab na feature/online-validation, integrada
por fast-forward ao develop SOMENTE no clone isolado. A correção começou em
feature/config-form-state a partir desse develop. Main permanece a4cd61a.
Runtime em Render/GitHub ainda f669ce2; esta correção ainda não foi publicada.

Antes de novo deploy: importar bundle na feature, confirmar pytest padrão,
publicar a feature e conferir sua CI. Depois publicar no Render e repetir dois
envios consecutivos no projeto E2E, restaurando texto e papel ao finalizar.
Não confundir CI verde antiga (688 passed / 3 skipped em f669ce2) com CI desta
correção. A antiga inclui PostgreSQL real; a nova execução ainda está pendente.
