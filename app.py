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
        except:
            return pd.DataFrame(columns=columnas)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_datos(df):
    with pd.ExcelWriter(FILE_PATH, engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

# -------------------------------
# CARGAR DATA
# -------------------------------
df = cargar_datos()

# -------------------------------
# FORMULARIO NUEVO REGISTRO
# -------------------------------
st.subheader("➕ Registrar evaluación")

with st.form("form_nuevo"):
    col1, col2, col3 = st.columns(3)

    with col1:
        mes = st.selectbox("MES", [
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
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
                f"P{i+1}", min_value=1.0, max_value=10.0, step=0.1, key=f"new_{i}"
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
        st.success("✅ Registro guardado")

# -------------------------------
# KPI
# -------------------------------
st.subheader("📈 Indicador de Satisfacción")

if not df.empty:
    respuestas = df[[f"P{i}" for i in range(1,11)]].values.flatten()
    respuestas = [r for r in respuestas if pd.notnull(r)]

    if len(respuestas) > 0:
        positivas = len([r for r in respuestas if r >= 8])
        porcentaje = (positivas / len(respuestas)) * 100
    else:
        porcentaje = 0

    estado = "🟢 Excelente" if porcentaje >= 90 else "🟡 Aceptable" if porcentaje >= 75 else "🔴 Crítico"

    col1, col2 = st.columns(2)
    col1.metric("% Satisfacción", f"{round(porcentaje,2)}%")
    col2.metric("Estado", estado)

# -------------------------------
# HISTORIAL
# -------------------------------
st.subheader("📋 Historial")

if not df.empty:
    df_reset = df.reset_index()
    st.dataframe(df_reset, use_container_width=True)

# -------------------------------
# ✏️ EDICIÓN
# -------------------------------
st.subheader("✏️ Editar registro")

if not df.empty:

    idx = st.number_input("Selecciona índice a editar",
                          min_value=0,
                          max_value=len(df_reset)-1,
                          step=1)

    fila = df_reset.loc[idx]

    with st.form("form_editar"):

        mes_e = st.selectbox("MES", [
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
        ], index=[
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
        ].index(fila["MES"]))

        fecha_e = st.date_input("FECHA", fila["FECHA DE EVALUACION"])
        cliente_e = st.text_input("CLIENTE", fila["CLIENTE EVALUADO"])

        preguntas_e = {}
        cols = st.columns(5)

        for i in range(10):
            with cols[i % 5]:
                preguntas_e[f"P{i+1}"] = st.number_input(
                    f"P{i+1}",
                    value=float(fila[f"P{i+1}"]),
                    min_value=1.0,
                    max_value=10.0,
                    step=0.1,
                    key=f"edit_{i}"
                )

        if st.form_submit_button("Actualizar"):
            df.loc[idx, "MES"] = mes_e
            df.loc[idx, "FECHA DE EVALUACION"] = fecha_e
            df.loc[idx, "CLIENTE EVALUADO"] = cliente_e

            for k, v in preguntas_e.items():
                df.loc[idx, k] = v

            guardar_datos(df)
            st.success("✅ Registro actualizado")

# -------------------------------
# 🗑️ ELIMINACIÓN
# -------------------------------
st.subheader("🗑️ Eliminar registro")

if not df.empty:
    fila_eliminar = st.number_input("Índice a eliminar",
                                   min_value=0,
                                   max_value=len(df_reset)-1,
                                   step=1)

    confirmar = st.checkbox("Confirmar eliminación")

    if st.button("Eliminar"):
        if confirmar:
            df = df.drop(index=fila_eliminar).reset_index(drop=True)
            guardar_datos(df)
            st.success("Registro eliminado")
        else:
            st.warning("Debes confirmar")

# -------------------------------
# GRÁFICO
# -------------------------------
if not df.empty:
    df["Promedio"] = df[[f"P{i}" for i in range(1,11)]].mean(axis=1)
    st.subheader("📊 Tendencia")
    st.line_chart(df["Promedio"])
