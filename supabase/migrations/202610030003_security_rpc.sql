-- Grants + RLS + RPCs transacionais. Sem acesso de escrita direto a valores/histórico.
begin;
create function apolo_private.create_profile() returns trigger
 language plpgsql security definer set search_path='' as $$
begin
 insert into public.profiles(id,nome,role)
 values(new.id,left(coalesce(new.raw_user_meta_data->>'nome',new.email,''),120),'operador');
 return new;
end $$;
revoke all on function apolo_private.create_profile() from public,anon,authenticated;
create trigger apolo_create_profile after insert on auth.users
 for each row execute function apolo_private.create_profile();
insert into public.profiles(id,nome,role)
 select id,left(coalesce(raw_user_meta_data->>'nome',email,''),120),'operador' from auth.users
 on conflict(id) do nothing;

create function apolo_private.initialize_project() returns trigger
 language plpgsql security definer set search_path='' as $$
begin
 insert into public.project_values(project_id,id_variavel,valor_real,valor_texto)
 select new.id,id_variavel,padrao_real,padrao_texto from public.variables;
 return new;
end $$;
revoke all on function apolo_private.initialize_project() from public,anon,authenticated;
create trigger apolo_initialize_project after insert on public.projects
 for each row execute function apolo_private.initialize_project();

grant select on public.profiles,public.variables,public.calculations,
 public.calculation_dependencies,public.projects,public.project_values,
 public.executions,public.execution_values to authenticated;
grant insert(nome,owner_id) on public.projects to authenticated;

create policy profiles_own on public.profiles for select to authenticated
 using(id=(select auth.uid()));
create policy variables_read on public.variables for select to authenticated
 using((select auth.uid()) is not null);
create policy calculations_read on public.calculations for select to authenticated
 using((select auth.uid()) is not null);
create policy dependencies_read on public.calculation_dependencies for select to authenticated
 using((select auth.uid()) is not null);
create policy projects_own on public.projects for select to authenticated
 using(owner_id=(select auth.uid()));
create policy projects_create on public.projects for insert to authenticated
 with check(owner_id=(select auth.uid()));
create policy project_values_own on public.project_values for select to authenticated
 using(exists(select 1 from public.projects p
              where p.id=project_id and p.owner_id=(select auth.uid())));
create policy executions_own on public.executions for select to authenticated
 using(user_id=(select auth.uid()) and exists(
   select 1 from public.projects p where p.id=project_id and p.owner_id=(select auth.uid())));
create policy execution_values_own on public.execution_values for select to authenticated
 using(exists(select 1 from public.executions e where e.id=execution_id
              and e.user_id=(select auth.uid())));

-- Helpers privados: chamadas de RPC definer sempre validam auth.uid real.
create function apolo_private.require_project(p_project_id uuid) returns void
 language plpgsql security definer set search_path='' as $$
begin
 if auth.uid() is null or not exists(
   select 1 from public.projects p join public.profiles pr on pr.id=p.owner_id
   where p.id=p_project_id and p.owner_id=auth.uid()
     and pr.role in ('operador','admin','desenvolvedor')
 ) then
   raise exception 'Projeto não autorizado' using errcode='42501';
 end if;
 -- Serializa cálculo/configuração por projeto para conservar valores atuais.
 perform 1 from public.projects where id=p_project_id for update;
end $$;
create function apolo_private.finite_number(p_value jsonb) returns double precision
 language plpgsql immutable set search_path='' as $$
declare v double precision;
begin
 if jsonb_typeof(p_value) is distinct from 'number' then
   raise exception 'Valor numérico inválido' using errcode='22023';
 end if;
 v := (p_value #>> '{}')::double precision;
 if v in ('NaN'::double precision,'Infinity'::double precision,'-Infinity'::double precision) then
   raise exception 'Valor não finito' using errcode='22023';
 end if;
 return v;
end $$;
revoke all on function apolo_private.require_project(uuid) from public,anon,authenticated;
revoke all on function apolo_private.finite_number(jsonb) from public,anon,authenticated;

create function public.apolo_save_execution(
 p_project_id uuid,p_id_calculo text,p_entradas jsonb,p_saidas jsonb
) returns uuid language plpgsql security definer set search_path='' as $$
declare
 v_id uuid := gen_random_uuid();
 v_expected text[];
 v_keys text[];
 v_item record;
 v_papel text;
 v_data jsonb;
 v_real double precision;
 v_variable public.variables%rowtype;
begin
 perform apolo_private.require_project(p_project_id);
 if not exists(select 1 from public.calculations where id_calculo=p_id_calculo and ativo) then
   raise exception 'Cálculo desconhecido' using errcode='22023';
 end if;
 if jsonb_typeof(p_entradas) is distinct from 'object'
    or jsonb_typeof(p_saidas) is distinct from 'object' then
   raise exception 'Snapshot inválido' using errcode='22023';
 end if;
 -- Exige exatamente os nomes auditados, sem campos externos/faltantes.
 foreach v_papel in array array['entrada','saida'] loop
   v_data := case when v_papel='entrada' then p_entradas else p_saidas end;
   select array_agg(v.nome order by v.nome) into v_expected
    from public.calculation_dependencies d join public.variables v using(id_variavel)
    where d.id_calculo=p_id_calculo and d.papel=v_papel;
   select array_agg(key order by key) into v_keys from jsonb_object_keys(v_data) as key;
   if v_keys is distinct from v_expected then
     raise exception 'Variáveis incompatíveis com o cálculo' using errcode='22023';
   end if;
 end loop;
 insert into public.executions(id,project_id,user_id,id_calculo,status)
 values(v_id,p_project_id,auth.uid(),p_id_calculo,'SUCESSO');
 foreach v_papel in array array['entrada','saida'] loop
   v_data := case when v_papel='entrada' then p_entradas else p_saidas end;
   for v_item in select key,value from jsonb_each(v_data) loop
     select * into strict v_variable from public.variables where nome=v_item.key;
     v_real := apolo_private.finite_number(v_item.value);
     insert into public.execution_values(
       execution_id,id_variavel,papel,valor_real,unidade_si)
     values(v_id,v_variable.id_variavel,v_papel,v_real,v_variable.unidade_si);
     update public.project_values set valor_real=v_real,valor_texto=null,atualizado_em=now()
      where project_id=p_project_id and id_variavel=v_variable.id_variavel;
     if not found then
       raise exception 'Projeto incompleto' using errcode='22023';
     end if;
   end loop;
 end loop;
 return v_id;
end $$;
revoke all on function public.apolo_save_execution(uuid,text,jsonb,jsonb)
 from public,anon,authenticated;
grant execute on function public.apolo_save_execution(uuid,text,jsonb,jsonb) to authenticated;

create function public.apolo_configure(p_project_id uuid,p_nome text,p_valor jsonb)
 returns void language plpgsql security definer set search_path='' as $$
declare v public.variables%rowtype; v_real double precision; v_text text;
begin
 perform apolo_private.require_project(p_project_id);
 if not exists(select 1 from public.profiles where id=auth.uid() and role in('admin','desenvolvedor')) then
   raise exception 'Configuração não autorizada' using errcode='42501';
 end if;
 select * into v from public.variables where nome=p_nome and not eh_saida;
 if not found then
   raise exception 'Variável de entrada desconhecida' using errcode='22023';
 end if;
 if v.tipo='REAL' then
   v_real := apolo_private.finite_number(p_valor);
 else
   if jsonb_typeof(p_valor) is distinct from 'string' then
     raise exception 'Texto inválido' using errcode='22023';
   end if;
   v_text := p_valor #>> '{}';
 end if;
 update public.project_values set valor_real=v_real,valor_texto=v_text,atualizado_em=now()
 where project_id=p_project_id and id_variavel=v.id_variavel;
 if not found then raise exception 'Projeto incompleto' using errcode='22023'; end if;
end $$;
revoke all on function public.apolo_configure(uuid,text,jsonb) from public,anon,authenticated;
grant execute on function public.apolo_configure(uuid,text,jsonb) to authenticated;

create function public.apolo_diagnostics(p_project_id uuid) returns jsonb
 language plpgsql security definer set search_path='' as $$
begin
 perform apolo_private.require_project(p_project_id);
 if not exists(select 1 from public.profiles where id=auth.uid() and role='desenvolvedor') then
   raise exception 'Diagnóstico não autorizado' using errcode='42501';
 end if;
 return jsonb_build_object('backend','supabase','project_id',p_project_id,
   'execucoes',(select count(*) from public.executions where project_id=p_project_id),
   'variaveis',(select count(*) from public.project_values where project_id=p_project_id));
end $$;
revoke all on function public.apolo_diagnostics(uuid) from public,anon,authenticated;
grant execute on function public.apolo_diagnostics(uuid) to authenticated;
-- Tornar funções novas visíveis ao PostgREST após a migration.
notify pgrst,'reload schema';
commit;
