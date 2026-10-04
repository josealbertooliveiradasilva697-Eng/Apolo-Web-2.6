-- VALIDAÇÃO MANUAL, NÃO MIGRATION. Somente no projeto Apolo autorizado.
-- Aprovação do usuário: testar ADMIN e DESENVOLVEDOR na conta indicada,
-- restaurando OPERADOR. As alterações abaixo ficam invisíveis a outras sessões
-- e são desfeitas pelo ROLLBACK, inclusive configurações e tentativas de INSERT.
-- Claims SQL controlados exercitam PostgreSQL/RLS/RPC, NÃO login/JWT HTTP.
begin;
do $$
declare alvo uuid; segundo uuid; p uuid; q uuid;
begin
 select pr.id into strict alvo from public.profiles pr join auth.users u on u.id=pr.id
 where u.email='josealberto290@outlook.com' and pr.role='operador';
 select id into strict p from public.projects
 where owner_id=alvo and nome='Validacao E2E 2026-10-03 A';
 select id,owner_id into strict q,segundo from public.projects where nome='Alberto2';
 if alvo=segundo or not exists(select 1 from public.profiles where id=segundo and role='operador') then
  raise exception 'Segunda conta independente com papel operador obrigatoria';
 end if;
 if (select count(*) from public.executions where project_id=p)<>6 then
  raise exception 'Projeto A deve conter as seis execucoes auditadas';
 end if;
 perform set_config('apolo.test_user',alvo::text,true);
 perform set_config('apolo.second_user',segundo::text,true);
 perform set_config('apolo.test_project',p::text,true);
 perform set_config('apolo.second_project',q::text,true);
end $$;

update public.profiles set role='admin' where id=current_setting('apolo.test_user')::uuid;
select set_config('request.jwt.claim.sub',current_setting('apolo.test_user'),true);
set local role authenticated;
do $$
declare p uuid:=current_setting('apolo.test_project')::uuid;
 q uuid:=current_setting('apolo.second_project')::uuid;
begin
 if (select count(*) from public.profiles)<>1
  or (select role from public.profiles where id=auth.uid())<>'admin' then
  raise exception 'ADMIN: perfil proprio esperado';
 end if;
 if (select count(*) from public.executions where project_id=p)<>6
  or exists(select 1 from public.projects where id=q)
  or exists(select 1 from public.project_values where project_id=q)
  or exists(select 1 from public.executions where project_id=q)
  or exists(select 1 from public.execution_values ev join public.executions e on e.id=ev.execution_id where e.project_id=q) then
  raise exception 'ADMIN: isolamento de SELECT falhou';
 end if;
 perform public.apolo_configure(p,'Pressão do ar','12345'::jsonb);
 if not exists(select 1 from public.project_values pv join public.variables v using(id_variavel)
  where pv.project_id=p and v.nome='Pressão do ar' and pv.valor_real=12345) then
  raise exception 'ADMIN: configurar projeto proprio falhou';
 end if;
 begin
  perform public.apolo_diagnostics(p);
  raise exception 'ADMIN: diagnostico deveria ser negado';
 exception when insufficient_privilege then null;
 end;
 begin
  perform public.apolo_configure(q,'Pressão do ar','12345'::jsonb);
  raise exception 'ADMIN: configuracao alheia deveria ser negada';
 exception when insufficient_privilege then null;
 end;
 begin
  perform public.apolo_save_execution(q,'CAL_SUST','{}','{}');
  raise exception 'ADMIN: gravacao alheia deveria ser negada';
 exception when insufficient_privilege then null;
 end;
 begin
  insert into public.projects(nome,owner_id) values('TESTE TRANSACIONAL SEM PERSISTENCIA',current_setting('apolo.second_user')::uuid);
  raise exception 'ADMIN: falsificacao de dono deveria ser negada';
 exception when insufficient_privilege then null;
 end;
 if has_table_privilege(current_user,'public.profiles','UPDATE') then
  raise exception 'ADMIN nao pode promover perfis pelo cliente';
 end if;
end $$;
reset role;

update public.profiles set role='desenvolvedor' where id=current_setting('apolo.test_user')::uuid;
set local role authenticated;
do $$
declare p uuid:=current_setting('apolo.test_project')::uuid;
 q uuid:=current_setting('apolo.second_project')::uuid;
 d jsonb;
begin
 if (select role from public.profiles where id=auth.uid())<>'desenvolvedor'
  or (select count(*) from public.profiles)<>1 then
  raise exception 'DESENVOLVEDOR: perfil proprio esperado';
 end if;
 perform public.apolo_configure(p,'Pressão do ar','23456'::jsonb);
 if not exists(select 1 from public.project_values pv join public.variables v using(id_variavel)
  where pv.project_id=p and v.nome='Pressão do ar' and pv.valor_real=23456) then
  raise exception 'DESENVOLVEDOR: configurar projeto proprio falhou';
 end if;
 d:=public.apolo_diagnostics(p);
 if (d->>'execucoes')::int<>6 or (d->>'variaveis')::int<>23 then
  raise exception 'DESENVOLVEDOR: diagnostico proprio inesperado';
 end if;
 if exists(select 1 from public.projects where id=q)
  or exists(select 1 from public.project_values where project_id=q)
  or exists(select 1 from public.executions where project_id=q)
  or exists(select 1 from public.execution_values ev join public.executions e on e.id=ev.execution_id where e.project_id=q) then
  raise exception 'DESENVOLVEDOR: isolamento de SELECT falhou';
 end if;
 begin
  perform public.apolo_diagnostics(q);
  raise exception 'DESENVOLVEDOR: diagnostico alheio deveria ser negado';
 exception when insufficient_privilege then null;
 end;
 begin
  perform public.apolo_configure(q,'Pressão do ar','12345'::jsonb);
  raise exception 'DESENVOLVEDOR: configurar projeto alheio deveria ser negado';
 exception when insufficient_privilege then null;
 end;
 begin
  perform public.apolo_save_execution(q,'CAL_SUST','{}','{}');
  raise exception 'DESENVOLVEDOR: gravacao alheia deveria ser negada';
 exception when insufficient_privilege then null;
 end;
end $$;
reset role;

select set_config('request.jwt.claim.sub',current_setting('apolo.second_user'),true);
set local role authenticated;
do $$
declare p uuid:=current_setting('apolo.test_project')::uuid;
 q uuid:=current_setting('apolo.second_project')::uuid;
begin
 if not exists(select 1 from public.projects where id=q)
  or exists(select 1 from public.projects where id=p)
  or exists(select 1 from public.project_values where project_id=p)
  or exists(select 1 from public.executions where project_id=p)
  or exists(select 1 from public.execution_values ev join public.executions e on e.id=ev.execution_id where e.project_id=p) then
  raise exception 'SEGUNDA CONTA: isolamento de SELECT falhou';
 end if;
 begin
  perform public.apolo_save_execution(p,'CAL_SUST','{}','{}');
  raise exception 'SEGUNDA CONTA: gravacao alheia deveria ser negada';
 exception when insufficient_privilege then null;
 end;
end $$;
reset role;
rollback;

-- Estes indicadores só são alcançados se todas as assertions anteriores passaram.
select true as matriz_papeis_aprovada, true as isolamento_duas_contas_aprovado,
 pr.role as papel_final
from public.profiles pr join auth.users u on u.id=pr.id
where u.email='josealberto290@outlook.com';
