-- Novo schema; não converte SQLite. Aplicar em projeto Supabase dedicado.
begin;
create schema if not exists apolo_private;
revoke all on schema apolo_private from public, anon, authenticated;
create table public.profiles (
 id uuid primary key references auth.users(id) on delete cascade,
 nome text not null default '',
 role text not null default 'operador' check (role in ('operador','admin','desenvolvedor')),
 created_at timestamptz not null default now()
);
create table public.variables (
 id_variavel text primary key, nome text not null unique,
 unidade_si text not null, unidade_codigo text not null,
 tipo text not null check (tipo in ('REAL','TEXT')), categoria text not null,
 eh_saida boolean not null, padrao_real double precision, padrao_texto text,
 descricao text not null,
 check ((tipo='REAL' and padrao_real is not null and padrao_texto is null)
     or (tipo='TEXT' and padrao_real is null and padrao_texto is not null))
);
create table public.calculations (
 id_calculo text primary key, nome text not null unique, versao text not null,
 formula text not null, unidade_saida text not null, descricao text not null,
 ativo boolean not null default true
);
create table public.calculation_dependencies (
 id_calculo text not null references public.calculations(id_calculo),
 id_variavel text not null references public.variables(id_variavel),
 papel text not null check (papel in ('entrada','saida')), ordem integer not null,
 primary key (id_calculo,id_variavel,papel)
);
create table public.projects (
 id uuid primary key default gen_random_uuid(),
 owner_id uuid not null references public.profiles(id) on delete cascade,
 nome text not null check (length(btrim(nome)) between 1 and 120),
 created_at timestamptz not null default now()
);
create index projects_owner on public.projects(owner_id);
create table public.project_values (
 project_id uuid not null references public.projects(id) on delete cascade,
 id_variavel text not null references public.variables(id_variavel),
 valor_real double precision, valor_texto text,
 atualizado_em timestamptz not null default now(),
 primary key (project_id,id_variavel),
 check ((valor_real is null) <> (valor_texto is null)),
 check (valor_real is null or valor_real not in
   ('NaN'::double precision,'Infinity'::double precision,'-Infinity'::double precision))
);
create table public.executions (
 id uuid primary key default gen_random_uuid(),
 project_id uuid not null references public.projects(id) on delete cascade,
 user_id uuid not null references public.profiles(id),
 id_calculo text not null references public.calculations(id_calculo),
 executado_em timestamptz not null default now(),
 status text not null check (status in ('SUCESSO','ERRO')), mensagem text
);
create index executions_project_date on public.executions(project_id,executado_em desc);
create index executions_user on public.executions(user_id);
create table public.execution_values (
 execution_id uuid not null references public.executions(id) on delete cascade,
 id_variavel text not null references public.variables(id_variavel),
 papel text not null check (papel in ('entrada','saida')),
 valor_real double precision not null check (valor_real not in
   ('NaN'::double precision,'Infinity'::double precision,'-Infinity'::double precision)),
 valor_texto text, unidade_si text not null,
 primary key (execution_id,id_variavel,papel)
);
-- As tabelas expostas começam fechadas, inclusive entre migrations.
alter table public.profiles enable row level security;
alter table public.variables enable row level security;
alter table public.calculations enable row level security;
alter table public.calculation_dependencies enable row level security;
alter table public.projects enable row level security;
alter table public.project_values enable row level security;
alter table public.executions enable row level security;
alter table public.execution_values enable row level security;
revoke all on public.profiles,public.variables,public.calculations,
 public.calculation_dependencies,public.projects,public.project_values,
 public.executions,public.execution_values from anon,authenticated;
commit;
