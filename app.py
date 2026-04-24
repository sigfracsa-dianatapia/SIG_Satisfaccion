import streamlit as st 
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="SIG - Indicadores", layout="wide")

# ============================================================
# 🔧 FUNCIÓN UNIVERSAL DE IMPORTACIÓN
# ============================================================
def importar_excel(df_actual, columnas_esperadas, guardar_func):
    st.subheader("📥 Importar datos desde Excel")

    archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

    if archivo is not None:
        try:
            df_nuevo = pd.read_excel(archivo)

            if not set(columnas_esperadas).issubset(set(df_nuevo.columns)):
                st.error("❌ El archivo no tiene la estructura correcta")
                return df_actual

            df_final = pd.concat([df_actual, df_nuevo], ignore_index=True)
            guardar_func(df_final)

            st.success(f"✅ {len(df_nuevo)} registros importados")
            return df_final

        except Exception as e:
            st.error(f"Error: {e}")

    return df_actual


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

    with st.form("form_prov"):
        proveedor = st.text_input("Proveedor")
        ruc = st.text_input("RUC")
        puntaje = st.number_input("Puntaje", 0.0, 5.0, step=0.1)

        if st.form_submit_button("Guardar"):
            estatus = "APROBADO" if puntaje >= 4 else "NO APROBADO"

            nuevo = pd.DataFrame([{
                "N°": len(df)+1,
                "MES": "N/A",
                "RUC": ruc,
                "PROVEEDOR": proveedor,
                "RUBRO": "",
                "PUNTAJE": puntaje,
                "ESTATUS": estatus,
                "CALIFICACION": "",
                "FECHA": datetime.today(),
                "REEVALUACION": "",
                "ESTADO": "",
                "CRITICIDAD": "CRITICO",
                "ESTADO PROV": "ACTIVO"
            }])

            df = pd.concat([df, nuevo], ignore_index=True)
            guardar(df)
            st.success("Guardado")

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

    st.data_editor(df)

    if not df.empty:
        sel = st.multiselect("Eliminar", df.index)
        if st.button("Eliminar seleccionados"):
            df = df.drop(sel)
            guardar(df)

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

    with st.form("form_cli"):
        cliente = st.text_input("Cliente")
        preguntas = {f"P{i}": st.number_input(f"P{i}",1.0,10.0) for i in range(1,11)}

        if st.form_submit_button("Guardar"):
            nuevo = {"CLIENTE EVALUADO":cliente}
            nuevo.update(preguntas)

            df = pd.concat([df, pd.DataFrame([nuevo])])
            guardar(df)

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
            st.write("Tendencia")
            st.line_chart(df["Promedio"])

        with col2:
            st.write("Promedio por Pregunta")
            st.bar_chart(df[[f"P{i}" for i in range(1,11)]].mean())

    st.dataframe(df)

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

    with st.form("form_prog"):
        cantidad = st.number_input("Total Programado", 0)
        cumplidos = st.number_input("Cumplidos", 0)

        if st.form_submit_button("Guardar"):
            porcentaje = (cumplidos/cantidad)*100 if cantidad>0 else 0

            nuevo = pd.DataFrame([{
                "N°": len(df)+1,
                "MES": "N/A",
                "CANTIDAD DE UNIDADES REQUERIDAS": cantidad,
                "CUMPLIDOS": cumplidos,
                "NO CUMPLIDOS": cantidad-cumplidos,
                "% CUMPLIMIENTO": porcentaje,
                "META": 95,
                "AÑO": datetime.today().year
            }])

            df = pd.concat([df, nuevo])
            guardar(df)

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
            if "% CUMPLIMIENTO" in df.columns:
                st.write("Tendencia")
                st.line_chart(df["% CUMPLIMIENTO"])

        with col2:
            st.write("Cumplidos vs No Cumplidos")
            st.bar_chart(df[["CUMPLIDOS","NO CUMPLIDOS"]])

    st.dataframe(df)
