import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================
# CONFIGURACIÓN
# =========================
FILE_PATH = "programacion_servicios.xlsx"
SHEET_NAME = "PROGRAMACION DE SERVICIO (1)-PP"

st.set_page_config(page_title="Programación de Servicios", layout="wide")
st.title("📊 Programación de Servicios - KPI Cumplimiento")

# =========================
# FUNCIONES
# =========================
def cargar_datos():
    columnas = [
        "N°","MES","INICIO DE SEMANA","FIN DE SEMANA",
        "FECHA DE REQUERIMIENTO","CLIENTE","PLANTA ORIGEN",
        "PLANTA DESTINO","CANTIDAD DE UNIDADES REQUERIDAS",
        "CUMPLIDOS","NO CUMPLIDOS","% CUMPLIMIENTO","META","AÑO"
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

# =========================
# CARGAR DATA
# =========================
df = cargar_datos()

# =========================
# FORMULARIO
# =========================
st.subheader("➕ Registrar Programación")

with st.form("form_programacion", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        numero = st.number_input("N°", min_value=1, step=1)
        mes = st.selectbox("MES", [
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
        ])
        anio = st.number_input("AÑO", min_value=2020, max_value=2100, value=datetime.today().year)

    with col2:
        inicio_semana = st.date_input("INICIO DE SEMANA")
        fin_semana = st.date_input("FIN DE SEMANA")
        fecha_req = st.date_input("FECHA DE REQUERIMIENTO")

    with col3:
        cliente = st.text_input("CLIENTE")
        planta_origen = st.text_input("PLANTA ORIGEN")
        planta_destino = st.text_input("PLANTA DESTINO")

    st.markdown("### 🚚 Unidades")
    col4, col5 = st.columns(2)

    with col4:
        cantidad = st.number_input("CANTIDAD DE UNIDADES REQUERIDAS", min_value=0)

    with col5:
        cumplidos = st.number_input("CUMPLIDOS", min_value=0)

    # =========================
    # CÁLCULOS AUTOMÁTICOS
    # =========================
    no_cumplidos = cantidad - cumplidos if cantidad >= cumplidos else 0
    porcentaje = (cumplidos / cantidad) * 100 if cantidad > 0 else 0
    META = 95

    st.info(f"📊 % Cumplimiento calculado: {porcentaje:.2f}%")

    if st.form_submit_button("Guardar"):

        nuevo = pd.DataFrame([{
            "N°": numero,
            "MES": mes,
            "INICIO DE SEMANA": inicio_semana,
            "FIN DE SEMANA": fin_semana,
            "FECHA DE REQUERIMIENTO": fecha_req,
            "CLIENTE": cliente,
            "PLANTA ORIGEN": planta_origen,
            "PLANTA DESTINO": planta_destino,
            "CANTIDAD DE UNIDADES REQUERIDAS": cantidad,
            "CUMPLIDOS": cumplidos,
            "NO CUMPLIDOS": no_cumplidos,
            "% CUMPLIMIENTO": porcentaje,
            "META": META,
            "AÑO": anio
        }])

        df = pd.concat([df, nuevo], ignore_index=True)
        guardar_datos(df)
        st.success("✅ Registro guardado correctamente")

# =========================
# KPI GENERAL
# =========================
st.subheader("📈 Indicador General")

if not df.empty:
    total_programado = df["CANTIDAD DE UNIDADES REQUERIDAS"].sum()
    total_cumplidos = df["CUMPLIDOS"].sum()

    indicador = (total_cumplidos / total_programado) * 100 if total_programado > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Programado", int(total_programado))
    col2.metric("Total Cumplido", int(total_cumplidos))
    col3.metric("% Cumplimiento", f"{indicador:.2f}%")

    if indicador >= 95:
        st.success("✅ Meta cumplida")
    else:
        st.error("❌ Meta no cumplida")

# =========================
# TABLA EDITABLE
# =========================
st.subheader("📋 Base de Datos")

if not df.empty:
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    if st.button("💾 Guardar cambios"):
        guardar_datos(edited_df)
        st.success("✅ Cambios guardados correctamente")
else:
    st.info("No hay datos registrados")

# =========================
# 🗑️ ELIMINACIÓN INTELIGENTE
# =========================
st.subheader("🗑️ Gestión de Eliminación de Registros")

if not df.empty:

    seleccion = st.multiselect(
        "Selecciona registros a eliminar",
        options=df.index,
        format_func=lambda x: (
            f"N° {df.loc[x,'N°']} | {df.loc[x,'CLIENTE']} | "
            f"{df.loc[x,'MES']} | Cumplimiento: {round(df.loc[x,'% CUMPLIMIENTO'],2)}%"
        )
    )

    col1, col2 = st.columns(2)

    # Eliminación parcial
    with col1:
        if st.button("Eliminar seleccionados"):
            if seleccion:
                df = df.drop(seleccion).reset_index(drop=True)
                guardar_datos(df)
                st.success(f"✅ Se eliminaron {len(seleccion)} registros")
            else:
                st.warning("⚠️ Selecciona al menos un registro")

    # Eliminación total
    with col2:
        st.markdown("### ⚠️ Eliminación total")

        confirmacion_1 = st.checkbox("Confirmo eliminar todos los registros")
        confirmacion_2 = st.checkbox("Entiendo que no se puede deshacer")

        if st.button("🧨 Borrar toda la base"):
            if confirmacion_1 and confirmacion_2:
                df = df.iloc[0:0]
                guardar_datos(df)
                st.error("🚨 Base de datos eliminada completamente")
            else:
                st.warning("⚠️ Debes confirmar ambas opciones")

else:
    st.info("📭 No hay registros para eliminar")

# =========================
# GRÁFICO
# =========================
if not df.empty:
    st.subheader("📊 Tendencia de Cumplimiento")
    st.line_chart(df["% CUMPLIMIENTO"])
