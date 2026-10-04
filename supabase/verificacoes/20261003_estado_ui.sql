-- Somente leitura: confirmar gravação da UI e estado de retorno do projeto A.
select pr.role as papel,
 pv.valor_texto as estado_projeto,
 (select count(*) from public.executions e where e.project_id=p.id) as execucoes
from public.profiles pr join auth.users u on u.id=pr.id
join public.projects p on p.owner_id=pr.id
join public.project_values pv on pv.project_id=p.id and pv.id_variavel='SP_text'
where u.email='josealberto290@outlook.com' and p.nome='Validacao E2E 2026-10-03 A';
