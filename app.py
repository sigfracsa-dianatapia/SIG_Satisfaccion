import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="SIG - Indicadores", layout="wide")

# =====================================================
# MENÚ PRINCIPAL
# =====================================================
st.sidebar.title("📊 SIG - Indicadores")
modulo = st.sidebar.selectbox("Selecciona módulo", [
    "Evaluación de Proveedores",
    "Satisfacción del Cliente"
])

# =====================================================
# =====================================================
# 🔵 MODULO 1: PROVEEDORES
# =====================================================
# =====================================================
if modulo == "Evaluación de Proveedores":

    st.title("📊 Evaluación de Proveedores")

    if "prov_data" not in st.session_state:
        st.session_state.prov_data = pd.DataFrame(columns=[
            "N°","MES","RUC","PROVEEDOR","RUBRO","PUNTAJE",
            "ESTATUS","CALIFICACION","FECHA","REEVALUACION",
            "ESTADO","CRITICIDAD","ESTADO PROV"
        ])

    df = st.session_state.prov_data

    # FORMULARIO
    st.subheader("📝 Registro")

    with st.form("form_prov"):

        col1, col2, col3 = st.columns(3)

        with col1:
            numero = st.number_input("N°", min_value=1, step=1)
            mes = st.selectbox("MES", [
                "Enero","Febrero","Marzo","Abril","Mayo","Junio",
                "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
            ])
            ruc = st.text_input("RUC")

        with col2:
            proveedor = st.text_input("PROVEEDOR")
            rubro = st.text_input("RUBRO")
            puntaje = st.number_input("PUNTAJE", 0, 100)

        with col3:
            estatus = st.selectbox("ESTATUS", ["Aprobado", "Desaprobado"])
            calificacion = st.text_input("CALIFICACIÓN")
            criticidad = st.selectbox("CRITICIDAD", ["Crítico", "No Crítico"])

        fecha = st.date_input("FECHA", datetime.today())
        reevaluacion = st.date_input("REEVALUACIÓN")
        estado = st.selectbox("ESTADO", ["Vigente", "No Vigente"])
        estado_prov = st.selectbox("ESTADO PROV", ["Activo", "Inactivo"])

        if st.form_submit_button("Guardar"):

            nueva = pd.DataFrame([{
                "N°": numero,
                "MES": mes,
                "RUC": ruc,
                "PROVEEDOR": proveedor,
                "RUBRO": rubro,
                "PUNTAJE": puntaje,
                "ESTATUS": estatus,
                "CALIFICACION": calificacion,
                "FECHA": fecha,
                "REEVALUACION": reevaluacion,
                "ESTADO": estado,
                "CRITICIDAD": criticidad,
                "ESTADO PROV": estado_prov
            }])

            st.session_state.prov_data = pd.concat([df, nueva], ignore_index=True)
            st.success("✅ Guardado")

    # KPI
    st.subheader("📈 Indicador")

    df = st.session_state.prov_data

    if not df.empty:
        total_criticos = df[df["CRITICIDAD"] == "Crítico"].shape[0]
        aprobados = df[(df["CRITICIDAD"] == "Crítico") & (df["ESTATUS"] == "Aprobado")].shape[0]

        indicador = (aprobados / total_criticos * 100) if total_criticos > 0 else 0

        st.metric("% Evaluación", f"{indicador:.2f}%")

        if indicador >= 95:
            st.success("Meta cumplida ✅")
        else:
            st.error("Meta no cumplida ❌")

    st.dataframe(df, use_container_width=True)

# =====================================================
# =====================================================
# 🟢 MODULO 2: SATISFACCIÓN DEL CLIENTE
# =====================================================
# =====================================================
elif modulo == "Satisfacción del Cliente":

    FILE_PATH = "satisfaccion_cliente.xlsx"
    SHEET_NAME = "SIG (1)"

    st.title("📊 Satisfacción del Cliente")

    # FUNCIONES
    def cargar_datos():
        columnas = [
            "MES", "FECHA DE EVALUACION", "CLIENTE EVALUADO",
            "P1","P2","P3","P4","P5","P6","P7","P8","P9","P10"
        ]
        if os.path.exists(FILE_PATH):
            try:
                return pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)
            except:
                return pd.DataFrame(columns=columnas)
        return pd.DataFrame(columns=columnas)

    def guardar_datos(df):
        with pd.ExcelWriter(FILE_PATH, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

    df = cargar_datos()

    # FORMULARIO
    st.subheader("➕ Registrar evaluación")

    with st.form("form_cliente"):

        col1, col2, col3 = st.columns(3)

        with col1:
            mes = st.selectbox("MES", [
                "Enero","Febrero","Marzo","Abril","Mayo","Junio",
                "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
            ])
        with col2:
            fecha = st.date_input("FECHA")
        with col3:
            cliente = st.text_input("CLIENTE")

        st.markdown("### Evaluación (1-10)")
        preguntas = {}
        cols = st.columns(5)

        for i in range(10):
            with cols[i % 5]:
                preguntas[f"P{i+1}"] = st.number_input(
                    f"P{i+1}", 1.0, 10.0, step=0.1, key=f"p{i}"
                )

        if st.form_submit_button("Guardar"):
            nueva = {
                "MES": mes,
                "FECHA DE EVALUACION": fecha,
                "CLIENTE EVALUADO": cliente
            }
            nueva.update(preguntas)

            df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
            guardar_datos(df)
            st.success("✅ Guardado")

    # KPI
    st.subheader("📈 Indicador")

    if not df.empty:
        respuestas = df[[f"P{i}" for i in range(1,11)]].values.flatten()
        respuestas = [r for r in respuestas if pd.notnull(r)]

        porcentaje = (len([r for r in respuestas if r >= 8]) / len(respuestas) * 100) if respuestas else 0

        estado = "🟢 Excelente" if porcentaje >= 90 else "🟡 Aceptable" if porcentaje >= 75 else "🔴 Crítico"

        col1, col2 = st.columns(2)
        col1.metric("% Satisfacción", f"{porcentaje:.2f}%")
        col2.metric("Estado", estado)

    # HISTORIAL
    st.subheader("📋 Historial")
    st.dataframe(df, use_container_width=True)

    # GRÁFICO
    if not df.empty:
        df["Promedio"] = df[[f"P{i}" for i in range(1,11)]].mean(axis=1)
        st.subheader("📊 Tendencia")
        st.line_chart(df["Promedio"])
