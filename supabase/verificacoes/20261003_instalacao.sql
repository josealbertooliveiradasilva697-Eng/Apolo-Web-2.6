-- Consulta somente leitura aplicada após as três migrations no projeto dedicado.
-- Não cria roles/auth.users; não deve usar o bootstrap de testes no Supabase.
with tabelas as (
 select c.oid,c.relrowsecurity
 from pg_class c join pg_namespace n on n.oid=c.relnamespace
 where n.nspname='public' and c.relkind='r'
 and c.relname in ('profiles','variables','calculations',
   'calculation_dependencies','projects','project_values',
   'executions','execution_values')
)
select
 (select count(*) from public.variables) as variaveis,
 (select count(*) from public.calculations) as calculos,
 (select count(*) from public.calculation_dependencies) as dependencias,
 (select count(*) from tabelas) as tabelas,
 (select count(*) from tabelas where relrowsecurity) as tabelas_rls,
 (select count(*) from pg_policies where schemaname='public') as politicas_rls,
 (select bool_and(not has_table_privilege('anon',oid,'SELECT')) from tabelas)
   as anon_sem_leitura,
 (select bool_and(not has_table_privilege('authenticated',oid,'UPDATE')) from tabelas)
   as cliente_sem_update_direto,
 not has_function_privilege('anon',
   'public.apolo_save_execution(uuid,text,jsonb,jsonb)','EXECUTE') as anon_sem_rpc,
 has_function_privilege('authenticated',
   'public.apolo_save_execution(uuid,text,jsonb,jsonb)','EXECUTE') as autenticado_pode_rpc;
