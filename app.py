import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="SIG - Indicadores", layout="wide")

# ============================================================
# 🔧 FUNCIÓN IMPORTAR EXCEL
# ============================================================
def importar_excel(df_actual, columnas_esperadas, guardar_func):
    st.subheader("📥 Importar datos desde Excel")
    archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

    if archivo is not None:
        try:
            df_nuevo = pd.read_excel(archivo)

            if not set(columnas_esperadas).issubset(set(df_nuevo.columns)):
                st.error("❌ Estructura incorrecta")
                return df_actual

            df_final = pd.concat([df_actual, df_nuevo], ignore_index=True)
            guardar_func(df_final)
            st.success(f"✅ {len(df_nuevo)} registros importados")
            return df_final

        except Exception as e:
            st.error(f"Error: {e}")

    return df_actual

# ============================================================
# 🔴 FUNCIÓN BORRAR TODO (GLOBAL)
# ============================================================
def borrar_todo(df, guardar_func):
    st.subheader("🧨 Borrar toda la base de datos")

    col1, col2 = st.columns(2)

    with col1:
        confirm1 = st.checkbox("Confirmo eliminar todos los registros")
    with col2:
        confirm2 = st.checkbox("Entiendo que no se puede deshacer")

    if st.button("🚨 Ejecutar borrado total"):
        if confirm1 and confirm2:
            df = df.iloc[0:0]
            guardar_func(df)
            st.error("🚨 Base de datos eliminada completamente")
            return df
        else:
            st.warning("⚠️ Debes confirmar ambas opciones")

    return df

# ============================================================
# 📌 MENÚ
# ============================================================
menu = st.sidebar.selectbox("Selecciona módulo", [
    "Proveedores",
    "Satisfacción Cliente",
    "Programación Servicios"
])

# ============================================================
# =================== PROVEEDORES =============================
# ============================================================
if menu == "Proveedores":

    FILE = "proveedores.csv"

    if not os.path.exists(FILE):
        pd.DataFrame(columns=[
            "N°","MES","RUC","PROVEEDOR","RUBRO","PUNTAJE",
            "ESTATUS","CALIFICACION","FECHA","REEVALUACION",
            "ESTADO","CRITICIDAD","ESTADO PROV"
        ]).to_csv(FILE, index=False)

    df = pd.read_csv(FILE)

    def guardar(df): df.to_csv(FILE, index=False)

    st.title("📊 Evaluación de Proveedores")

    columnas = [
        "N°","MES","RUC","PROVEEDOR","RUBRO","PUNTAJE",
        "ESTATUS","CALIFICACION","FECHA","REEVALUACION",
        "ESTADO","CRITICIDAD","ESTADO PROV"
    ]

    df = importar_excel(df, columnas, guardar)

    # KPI
    criticos = df[df["CRITICIDAD"]=="CRITICO"]
    indicador = (len(criticos[criticos["ESTATUS"]=="APROBADO"]) / len(criticos))*100 if len(criticos)>0 else 0
    st.metric("Indicador %", f"{indicador:.2f}%")

    # 🔥 DASHBOARD
    st.subheader("📊 Dashboard Proveedores")

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.write("Distribución de Estatus")
            st.bar_chart(df["ESTATUS"].value_counts())

        with col2:
            st.write("Promedio de Puntaje")
            st.metric("Promedio", f"{df['PUNTAJE'].mean():.2f}")

    # TABLA
    st.data_editor(df)

    # BORRAR TODO
    df = borrar_todo(df, guardar)

# ============================================================
# ================= SATISFACCIÓN ==============================
# ============================================================
elif menu == "Satisfacción Cliente":

    FILE = "satisfaccion.xlsx"

    def cargar():
        if os.path.exists(FILE):
            return pd.read_excel(FILE)
        return pd.DataFrame()

    def guardar(df):
        df.to_excel(FILE, index=False)

    df = cargar()

    st.title("😊 Satisfacción del Cliente")

    columnas = ["MES","FECHA DE EVALUACION","CLIENTE EVALUADO"] + [f"P{i}" for i in range(1,11)]
    df = importar_excel(df, columnas, guardar)

    if not df.empty:
        vals = df[[f"P{i}" for i in range(1,11)]].values.flatten()
        vals = [v for v in vals if pd.notnull(v)]
        indicador = (len([v for v in vals if v>=8])/len(vals))*100 if vals else 0
        st.metric("% Satisfacción", f"{indicador:.2f}%")

    # 🔥 DASHBOARD
    st.subheader("📊 Dashboard Satisfacción")

    if not df.empty:
        df["Promedio"] = df[[f"P{i}" for i in range(1,11)]].mean(axis=1)

        col1, col2 = st.columns(2)

        with col1:
            st.write("Tendencia de Satisfacción")
            st.line_chart(df["Promedio"])

        with col2:
            st.write("Distribución de respuestas")
            st.bar_chart(df[[f"P{i}" for i in range(1,11)]].mean())

    st.dataframe(df)

    # BORRAR TODO
    df = borrar_todo(df, guardar)

# ============================================================
# ================= PROGRAMACIÓN ==============================
# ============================================================
elif menu == "Programación Servicios":

    FILE = "programacion.xlsx"

    def cargar():
        if os.path.exists(FILE):
            return pd.read_excel(FILE)
        return pd.DataFrame()

    def guardar(df):
        df.to_excel(FILE, index=False)

    df = cargar()

    st.title("📊 Programación de Servicios")

    columnas = [
        "N°","MES","CANTIDAD DE UNIDADES REQUERIDAS",
        "CUMPLIDOS","NO CUMPLIDOS","% CUMPLIMIENTO","META","AÑO"
    ]

    df = importar_excel(df, columnas, guardar)

    if not df.empty:
        total = df["CANTIDAD DE UNIDADES REQUERIDAS"].sum()
        cumplidos = df["CUMPLIDOS"].sum()
        indicador = (cumplidos/total)*100 if total>0 else 0
        st.metric("% Cumplimiento", f"{indicador:.2f}%")

    # 🔥 DASHBOARD
    st.subheader("📊 Dashboard Cumplimiento")

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.write("Tendencia de Cumplimiento")
            if "% CUMPLIMIENTO" in df.columns:
                st.line_chart(df["% CUMPLIMIENTO"])

        with col2:
            st.write("Comparación Cumplidos vs No Cumplidos")
            st.bar_chart(df[["CUMPLIDOS","NO CUMPLIDOS"]])

    st.dataframe(df)

    # BORRAR TODO
    df = borrar_todo(df, guardar)
