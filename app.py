import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SIG Indicadores", layout="wide")

# =========================================
# MENÚ
# =========================================
st.sidebar.title("📊 SIG - Indicadores")

modulo = st.sidebar.radio("Selecciona módulo", [
    "Evaluación de Proveedores",
    "Satisfacción del Cliente"
])

# =========================================
# ================= PROVEEDORES ============
# =========================================
if modulo == "Evaluación de Proveedores":

    FILE_NAME = "proveedores.csv"

    st.title("📊 Evaluación de Proveedores")

    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
    else:
        df = pd.DataFrame(columns=["Proveedor","Critico","Estado"])

    def guardar(df):
        df.to_csv(FILE_NAME, index=False)

    def indicador(df):
        total = df[df["Critico"]=="SI"].shape[0]
        aprobados = df[(df["Critico"]=="SI") & (df["Estado"]=="Aprobado")].shape[0]

        if total == 0:
            return 0,0,0

        return (aprobados/total)*100, aprobados, total

    # FORM
    st.subheader("➕ Registrar proveedor")

    with st.form("form_prov"):
        proveedor = st.text_input("Proveedor")
        critico = st.selectbox("¿Crítico?", ["SI","NO"])
        estado = st.selectbox("Estado", ["Aprobado","No Aprobado"])

        if st.form_submit_button("Guardar"):
            nuevo = pd.DataFrame([{
                "Proveedor": proveedor,
                "Critico": critico,
                "Estado": estado
            }])

            df = pd.concat([df, nuevo], ignore_index=True)
            guardar(df)
            st.success("Guardado")

    # KPI
    st.subheader("📈 Indicador")

    porcentaje, aprobados, total = indicador(df)

    c1,c2,c3 = st.columns(3)
    c1.metric("Críticos", total)
    c2.metric("Aprobados", aprobados)
    c3.metric("%", f"{porcentaje:.2f}%")

    if porcentaje >= 95:
        st.success("Meta cumplida")
    else:
        st.error("Meta no cumplida")

    st.dataframe(df)

# =========================================
# ========== SATISFACCIÓN ==================
# =========================================
elif modulo == "Satisfacción del Cliente":

    FILE_PATH = "satisfaccion_cliente.xlsx"
    SHEET_NAME = "SIG (1)"

    st.title("📊 Satisfacción del Cliente")

    def cargar():
        columnas = [
            "MES","FECHA","CLIENTE",
            "P1","P2","P3","P4","P5",
            "P6","P7","P8","P9","P10"
        ]
        if os.path.exists(FILE_PATH):
            try:
                return pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)
            except:
                return pd.DataFrame(columns=columnas)
        return pd.DataFrame(columns=columnas)

    def guardar(df):
        with pd.ExcelWriter(FILE_PATH, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

    df = cargar()

    # FORM
    st.subheader("➕ Registrar evaluación")

    with st.form("form_sat"):

        col1,col2,col3 = st.columns(3)

        with col1:
            mes = st.selectbox("MES", [
                "Enero","Febrero","Marzo","Abril","Mayo","Junio",
                "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
            ])
        with col2:
            fecha = st.date_input("Fecha")
        with col3:
            cliente = st.text_input("Cliente")

        st.markdown("### Evaluación (1-10)")

        preguntas = {}
        cols = st.columns(5)

        for i in range(10):
            with cols[i % 5]:
                preguntas[f"P{i+1}"] = st.number_input(
                    f"P{i+1}", 1.0, 10.0, 8.0, key=f"p{i}"
                )

        if st.form_submit_button("Guardar"):
            nuevo = {
                "MES": mes,
                "FECHA": fecha,
                "CLIENTE": cliente
            }
            nuevo.update(preguntas)

            df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
            guardar(df)
            st.success("Guardado")

    # KPI
    st.subheader("📈 Indicador")

    if not df.empty:

        respuestas = df[[f"P{i}" for i in range(1,11)]].values.flatten()
        respuestas = [r for r in respuestas if pd.notnull(r)]

        if len(respuestas) > 0:
            positivas = len([r for r in respuestas if r >= 8])
            porcentaje = (positivas / len(respuestas)) * 100
        else:
            porcentaje = 0

        estado = "🟢" if porcentaje >= 90 else "🟡" if porcentaje >= 75 else "🔴"

        c1,c2 = st.columns(2)
        c1.metric("% Satisfacción", f"{porcentaje:.2f}%")
        c2.metric("Estado", estado)

    # HISTORIAL
    st.subheader("📋 Historial")
    st.dataframe(df)

    # GRAFICO
    if not df.empty:
        df["Promedio"] = df[[f"P{i}" for i in range(1,11)]].mean(axis=1)
        st.subheader("📊 Tendencia")
        st.line_chart(df["Promedio"])
