import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="SIG - Dashboard", layout="wide")

# ============================================================
# 📌 MENÚ
# ============================================================
menu = st.sidebar.selectbox("Selecciona vista", [
    "Dashboard Gerencial",
    "Proveedores",
    "Satisfacción Cliente",
    "Programación Servicios"
])

# ============================================================
# 📂 CARGA DE DATOS
# ============================================================
def cargar_csv(file):
    return pd.read_csv(file) if os.path.exists(file) else pd.DataFrame()

def cargar_excel(file):
    return pd.read_excel(file) if os.path.exists(file) else pd.DataFrame()

df_prov = cargar_csv("proveedores.csv")
df_cli = cargar_excel("satisfaccion.xlsx")
df_prog = cargar_excel("programacion.xlsx")

# ============================================================
# 🧠 DASHBOARD GERENCIAL
# ============================================================
if menu == "Dashboard Gerencial":

    st.title("📊 Dashboard Gerencial SIG")

    col1, col2, col3 = st.columns(3)

    # ================= PROVEEDORES =================
    with col1:
        st.subheader("Proveedores")

        if not df_prov.empty:
            criticos = df_prov[df_prov["CRITICIDAD"] == "CRITICO"]
            total = len(criticos)
            aprobados = len(criticos[criticos["ESTATUS"] == "APROBADO"])
            indicador = (aprobados / total) * 100 if total > 0 else 0

            st.metric("Indicador", f"{indicador:.2f}%")

            if indicador >= 95:
                st.success("🟢 Cumple")
            elif indicador >= 85:
                st.warning("🟡 Riesgo")
            else:
                st.error("🔴 Crítico")

        else:
            st.info("Sin datos")

    # ================= CLIENTES =================
    with col2:
        st.subheader("Satisfacción")

        if not df_cli.empty:
            preguntas = [f"P{i}" for i in range(1, 11)]
            valores = df_cli[preguntas].values.flatten()
            valores = [v for v in valores if pd.notnull(v)]

            indicador = (len([v for v in valores if v >= 8]) / len(valores)) * 100 if valores else 0

            st.metric("Satisfacción", f"{indicador:.2f}%")

            if indicador >= 90:
                st.success("🟢 Excelente")
            elif indicador >= 75:
                st.warning("🟡 Aceptable")
            else:
                st.error("🔴 Crítico")

        else:
            st.info("Sin datos")

    # ================= PROGRAMACIÓN =================
    with col3:
        st.subheader("Cumplimiento")

        if not df_prog.empty:
            total = df_prog["CANTIDAD DE UNIDADES REQUERIDAS"].sum()
            cumplidos = df_prog["CUMPLIDOS"].sum()
            indicador = (cumplidos / total) * 100 if total > 0 else 0

            st.metric("Cumplimiento", f"{indicador:.2f}%")

            if indicador >= 95:
                st.success("🟢 Cumple")
            elif indicador >= 85:
                st.warning("🟡 Riesgo")
            else:
                st.error("🔴 Crítico")

        else:
            st.info("Sin datos")

    st.markdown("---")

    # ========================================================
    # 📊 TENDENCIAS
    # ========================================================
    st.subheader("📈 Tendencias")

    col1, col2 = st.columns(2)

    with col1:
        if not df_prog.empty and "% CUMPLIMIENTO" in df_prog.columns:
            st.write("Cumplimiento de Servicios")
            st.line_chart(df_prog["% CUMPLIMIENTO"])

    with col2:
        if not df_cli.empty:
            df_cli["Promedio"] = df_cli[[f"P{i}" for i in range(1, 11)]].mean(axis=1)
            st.write("Satisfacción del Cliente")
            st.line_chart(df_cli["Promedio"])

# ============================================================
# 📊 MÓDULOS (SIMPLIFICADOS)
# ============================================================
elif menu == "Proveedores":
    st.title("📊 Proveedores")
    st.dataframe(df_prov)

elif menu == "Satisfacción Cliente":
    st.title("😊 Satisfacción Cliente")
    st.dataframe(df_cli)

elif menu == "Programación Servicios":
    st.title("📊 Programación Servicios")
    st.dataframe(df_prog)
