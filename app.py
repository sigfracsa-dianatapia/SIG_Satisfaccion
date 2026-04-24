import streamlit as st
import pandas as pd
import os

# -------------------------------
# CONFIGURACIÓN
# -------------------------------
FILE_PATH = "satisfaccion_cliente.xlsx"
SHEET_NAME = "SIG (1)"

st.set_page_config(page_title="Satisfacción del Cliente", layout="wide")

st.title("📊 Evaluación de Satisfacción del Cliente")

# -------------------------------
# FUNCIONES
# -------------------------------

def cargar_datos():
    columnas = [
        "MES", "FECHA DE EVALUACION", "CLIENTE EVALUADO",
        "P1", "P2", "P3", "P4", "P5",
        "P6", "P7", "P8", "P9", "P10"
    ]

    if os.path.exists(FILE_PATH):
        try:
            return pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)
        except Exception:
            return pd.DataFrame(columns=columnas)
    else:
        return pd.DataFrame(columns=columnas)


def guardar_datos(df):
    try:
        with pd.ExcelWriter(FILE_PATH, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    except ImportError:
        st.error("❌ Falta instalar openpyxl. Agrega en requirements.txt o ejecuta: pip install openpyxl")


# -------------------------------
# CARGAR DATA
# -------------------------------
df = cargar_datos()

# -------------------------------
# FORMULARIO
# -------------------------------
st.subheader("➕ Registrar evaluación")

with st.form("form_satisfaccion"):

    col1, col2, col3 = st.columns(3)

    with col1:
        mes = st.selectbox("MES", [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo",
            "Junio", "Julio", "Agosto", "Septiembre",
            "Octubre", "Noviembre", "Diciembre"
        ])

    with col2:
        fecha = st.date_input("FECHA DE EVALUACIÓN")

    with col3:
        cliente = st.text_input("CLIENTE EVALUADO")

    st.markdown("### 📋 Evaluación (1 a 10)")

    preguntas = {}
    cols = st.columns(5)

    for i in range(10):
        with cols[i % 5]:
            preguntas[f"P{i+1}"] = st.number_input(
                f"P{i+1}",
                min_value=1.0,
                max_value=10.0,
                step=0.1,
                key=f"p{i+1}"
            )

    submitted = st.form_submit_button("Guardar")

    if submitted:

        # Validación básica
        if cliente.strip() == "":
            st.warning("⚠️ Ingresa el nombre del cliente")
        else:
            nueva_fila = {
                "MES": mes,
                "FECHA DE EVALUACION": fecha,
                "CLIENTE EVALUADO": cliente
            }

            nueva_fila.update(preguntas)

            df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

            guardar_datos(df)

            st.success("✅ Evaluación guardada correctamente")

# -------------------------------
# KPI SATISFACCIÓN (ISO REAL)
# -------------------------------
st.subheader("📈 Indicador de Satisfacción")

if not df.empty:

    try:
        respuestas = df[[f"P{i}" for i in range(1, 11)]].values.flatten()

        # Limpiar posibles nulos
        respuestas = [r for r in respuestas if pd.notnull(r)]

        total_respuestas = len(respuestas)

        if total_respuestas > 0:
            positivas = len([r for r in respuestas if r >= 8])
            porcentaje = (positivas / total_respuestas) * 100
        else:
            porcentaje = 0

        # Semáforo
        if porcentaje >= 90:
            estado = "🟢 Excelente"
        elif porcentaje >= 75:
            estado = "🟡 Aceptable"
        else:
            estado = "🔴 Crítico"

        col1, col2 = st.columns(2)

        col1.metric("% Satisfacción", f"{round(porcentaje,2)}%")
        col2.metric("Estado", estado)

    except Exception as e:
        st.error(f"Error en cálculo del KPI: {e}")

# -------------------------------
# TABLA
# -------------------------------
st.subheader("📋 Historial de evaluaciones")
st.dataframe(df, use_container_width=True)

# -------------------------------
# GRÁFICO
# -------------------------------
if not df.empty:
    try:
        df["Promedio"] = df[[f"P{i}" for i in range(1, 11)]].mean(axis=1)
        st.subheader("📊 Tendencia de satisfacción (Promedio por evaluación)")
        st.line_chart(df["Promedio"])
    except:
        st.info("No se pudo generar el gráfico")

# -------------------------------
# ALERTA AUTOMÁTICA
# -------------------------------
if not df.empty and 'porcentaje' in locals():
    if porcentaje < 75:
        st.error("🚨 Nivel de satisfacción bajo - Se recomienda generar acción correctiva")