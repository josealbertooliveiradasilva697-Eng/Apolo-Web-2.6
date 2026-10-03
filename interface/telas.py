import csv
import io
import json
import streamlit as st
from auth.roles import Acao, permitido
from core.catalogo import CATALOGO_CALCULOS, CATALOGO_VARIAVEIS
from database.repository import inspecionar_arquivo


def calculos(servico):
    st.subheader("Novo cálculo")
    id_calculo = st.selectbox("Equação", list(CATALOGO_CALCULOS), format_func=lambda c: CATALOGO_CALCULOS[c]["nome"])
    meta = CATALOGO_CALCULOS[id_calculo]
    st.caption(meta["formula"])
    valores = {r["nome"]:r["valor_real"] if r["tipo"]=="REAL" else r["valor_texto"] for r in servico.consultar()}
    with st.form(f"calculo_{servico.repo.path.name}_{id_calculo}"):
        entradas = {}
        for nome in meta["entradas"]:
            variavel = CATALOGO_VARIAVEIS[nome]
            valor = valores.get(nome)
            valor = variavel["padrao"] if valor is None else valor
            entradas[nome] = st.number_input(
                f"{nome} ({variavel['unidade_si']})", value=float(valor),
                format="%.10g", disabled=nome=="gravidade",
                help=variavel["descricao"],
                key=f"entrada:{servico.repo.path.name}:{id_calculo}:{variavel['id_variavel']}",
            )
        enviar = st.form_submit_button("Calcular e salvar", type="primary")
    if enviar:
        try:
            resultado = servico.executar(id_calculo, entradas)
            st.session_state["ultimo_resultado"] = resultado
            st.session_state["banco_resultado"] = str(servico.repo.path)
        except (ValueError, PermissionError) as exc:
            st.session_state.pop("ultimo_resultado",None)
            st.error(str(exc))
        else:
            st.success(f"Cálculo salvo. Execução {resultado['id_execucao']}.")
    resultado = st.session_state.get("ultimo_resultado")
    if resultado and resultado["id_calculo"]==id_calculo and st.session_state.get("banco_resultado")==str(servico.repo.path):
        for nome,valor in resultado["saidas"].items():
            st.metric(nome, f"{valor:.10g} {CATALOGO_VARIAVEIS[nome]['unidade_si']}")
        st.download_button("Baixar resultado (JSON)",json.dumps(resultado,ensure_ascii=False,indent=2),file_name=f"apolo_execucao_{resultado['id_execucao']}.json",mime="application/json")
    if id_calculo=="CAL_BREG":
        st.caption("Consumo específico em s⁻¹. Sustentação e arrasto podem ser preenchidos com os resultados salvos dos cálculos anteriores.")


def historico(servico):
    st.subheader("Histórico de execuções")
    linhas = servico.historico()
    if not linhas:
        st.info("Nenhum cálculo registrado neste banco.")
        return
    st.caption("Últimas 200 execuções do banco selecionado.")
    st.dataframe(linhas,hide_index=True,width="stretch")
    id_exec = st.selectbox("Detalhar execução",[r["id_execucao"] for r in linhas])
    detalhes = servico.detalhe(id_exec)
    st.dataframe(detalhes,hide_index=True,width="stretch")
    texto = io.StringIO()
    writer = csv.DictWriter(texto, fieldnames=list(detalhes[0]) if detalhes else ["id_execucao"])
    writer.writeheader()
    writer.writerows(detalhes)
    st.download_button("Baixar detalhes (CSV)",texto.getvalue().encode("utf-8-sig"),file_name=f"apolo_execucao_{id_exec}.csv",mime="text/csv")


def banco(servico):
    st.subheader("Banco de variáveis")
    linhas = servico.consultar()
    col1,col2 = st.columns(2)
    mostrar_entradas=col1.checkbox("Mostrar entradas",value=True)
    mostrar_saidas=col2.checkbox("Mostrar resultados",value=True)
    selecionadas = [r for r in linhas if (mostrar_saidas if r["eh_saida"] else mostrar_entradas)]
    st.dataframe(selecionadas,hide_index=True,width="stretch")
    if st.checkbox("Mostrar gráfico",value=False):
        unidades = sorted({r["unidade_si"] for r in selecionadas if r["tipo"]=="REAL"})
        if unidades:
            unidade=st.selectbox("Unidade do gráfico",unidades)
            # Uma unidade por gráfico evita comparar grandezas incompatíveis.
            chart=[{"Variável":r["nome"],"Valor":r["valor_real"]} for r in selecionadas if r["tipo"]=="REAL" and r["unidade_si"]==unidade]
            st.bar_chart(chart,x="Variável",y="Valor",horizontal=True)


def administracao(servico):
    st.subheader("Configurações de entrada")
    if not permitido(servico.usuario, Acao.CONFIGURAR):
        st.error("Seu perfil não permite esta operação.")
        return
    linhas=[r for r in servico.consultar() if not r["eh_saida"]]
    nome=st.selectbox("Variável",[r["nome"] for r in linhas])
    row=next(r for r in linhas if r["nome"]==nome)
    with st.form(f"config_{servico.repo.path.name}_{row['id_variavel']}"):
        if row["tipo"]=="REAL":
            valor=st.number_input(f"Valor ({row['unidade_si']})",value=float(row["valor_real"] or 0),format="%.10g")
        else:
            valor=st.text_input("Valor",value=row["valor_texto"] or "")
        enviar=st.form_submit_button("Salvar configuração")
    if enviar:
        try:
            servico.configurar(nome,valor)
        except (ValueError,PermissionError) as exc:
            st.error(str(exc))
        else:
            # Invalida formulários existentes para carregar o novo valor do banco.
            for chave in list(st.session_state):
                if chave.startswith("entrada:"):
                    del st.session_state[chave]
            st.success("Configuração salva.")
    st.caption("Papéis preparados para integração futura com Supabase. Gestão de usuários será acrescentada com a autenticação.")


def diagnosticos(servico):
    st.subheader("Diagnóstico local")
    if not permitido(servico.usuario, Acao.DIAGNOSTICAR):
        st.error("Seu perfil não permite esta operação.")
        return
    st.json(inspecionar_arquivo(servico.repo.path))
