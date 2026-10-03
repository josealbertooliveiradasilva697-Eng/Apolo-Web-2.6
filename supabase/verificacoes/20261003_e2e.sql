-- Somente leitura; escopo: dois projetos criados pela validação no navegador.
-- Não inclui e-mails, senhas ou tokens. Não promove papéis e não altera dados.
with referencias(id_calculo,esperado) as (
 values ('CAL_SUST',12250.0::double precision),('CAL_ARR',612.5),
 ('CAL_EMP',4000.0),('CAL_NEWTON',2000.0),('CAL_BER',104057.975),
 ('CAL_BREG',2231435.5131420977)
), projetos as (
 select * from public.projects
 where nome in ('Validacao E2E 2026-10-03 A','Validacao E2E 2026-10-03 B')
), resumo as (
 select p.nome,
 (select count(*) from public.project_values v where v.project_id=p.id) as variaveis,
 (select count(*) from public.executions e where e.project_id=p.id) as execucoes,
 (select count(distinct e.id_calculo) from public.executions e where e.project_id=p.id) as calculos_distintos,
 (select bool_and(e.user_id=p.owner_id and e.status='SUCESSO')
  from public.executions e where e.project_id=p.id) as dono_e_sucesso,
 (select count(*) from public.execution_values v join public.executions e
  on e.id=v.execution_id where e.project_id=p.id) as valores_snapshot,
 (select jsonb_agg(jsonb_build_object('calculo',e.id_calculo,'resultado',v.valor_real,
  'unidade',v.unidade_si,'equivalente',
  abs(v.valor_real-r.esperado)<=greatest(abs(r.esperado),1)*1e-12)
  order by e.id_calculo)
  from public.executions e join public.execution_values v on v.execution_id=e.id
  join referencias r on r.id_calculo=e.id_calculo
  where e.project_id=p.id and v.papel='saida') as resultados
 from projetos p
)
select jsonb_build_object(
 'profiles', (select count(*) from public.profiles),
 'profiles_operadores', (select count(*) from public.profiles where role='operador'),
 'projetos_teste', (select jsonb_agg(to_jsonb(resumo) order by nome) from resumo)
) as auditoria_e2e;
