-- Somente leitura: conferir a conta autorizada e os donos dos projetos E2E.
-- Não lê credenciais, hashes de senha ou tokens. Não altera perfis.
select pr.id, pr.role,
 u.email='josealberto290@outlook.com' as conta_autorizada,
 u.email_confirmed_at is not null as email_confirmado,
 (select count(*) from public.projects p where p.owner_id=pr.id) as projetos
from public.profiles pr join auth.users u on u.id=pr.id
order by pr.id;
