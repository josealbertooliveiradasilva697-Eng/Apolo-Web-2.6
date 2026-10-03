-- Diagnóstico limitado ao projeto A criado pelo teste, sem mudanças persistentes.
-- Usa o auth.uid() real do Supabase com claims SQL de teste, NÃO um login HTTP.
-- Os papéis/profile/grants não são modificados. Transação sempre termina ROLLBACK.
begin;
do $$
begin
 if (select count(*) from public.projects where nome='Validacao E2E 2026-10-03 A')<>1 then
  raise exception 'Projeto de teste inexistente ou ambiguo';
 end if;
 if not exists (select 1 from public.projects p join public.profiles pr on pr.id=p.owner_id
  where p.nome='Validacao E2E 2026-10-03 A' and pr.role='operador') then
  raise exception 'Perfil esperado: operador';
 end if;
end $$;
select set_config('apolo.test_project',id::text,true),
 set_config('request.jwt.claim.sub',owner_id::text,true)
from public.projects where nome='Validacao E2E 2026-10-03 A';
set local role authenticated;
do $$
declare p uuid:=current_setting('apolo.test_project')::uuid;
begin
 if auth.uid() is null or (select count(*) from public.projects where id=p)<>1 then
  raise exception 'Operador nao consegue consultar seu projeto';
 end if;
 if (select count(*) from public.executions where project_id=p)<>6 then
  raise exception 'Historico inesperado';
 end if;
 if has_table_privilege(current_user,'public.profiles','UPDATE') then
  raise exception 'Cliente nao pode promover o proprio perfil';
 end if;
 begin
  perform public.apolo_configure(p,'Pressão do ar','12345'::jsonb);
  raise exception 'FALHA: operador conseguiu configurar';
 exception when insufficient_privilege then null;
 end;
 begin
  perform public.apolo_diagnostics(p);
  raise exception 'FALHA: operador conseguiu diagnosticar';
 exception when insufficient_privilege then null;
 end;
end $$;
rollback;
select true as consulta_propria_permitida,
 true as configurar_negado_42501,
 true as diagnosticar_negado_42501,
 true as promover_perfil_sem_grant,
 true as sem_mudancas_persistentes;
