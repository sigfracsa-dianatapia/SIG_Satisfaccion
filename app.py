import streamlit as st
import pandas as pd
from datetime import datetime
import os

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(page_title="SIG - Indicadores", layout="wide")

menu = st.sidebar.selectbox("📌 Selecciona módulo", [
    "Evaluación de Proveedores",
    "Satisfacción del Cliente"
])

# ============================================================
# =================== MODULO 1: PROVEEDORES ===================
# ============================================================
if menu == "Evaluación de Proveedores":

    FILE_NAME = "proveedores.csv"

    if not os.path.exists(FILE_NAME):
        df_init = pd.DataFrame(columns=[
            "N°","MES","RUC","PROVEEDOR","RUBRO","PUNTAJE",
            "ESTATUS","CALIFICACION","FECHA","REEVALUACION",
            "ESTADO","CRITICIDAD","ESTADO PROV"
        ])
        df_init.to_csv(FILE_NAME, index=False)

    df = pd.read_csv(FILE_NAME)

    st.title("📊 Evaluación de Proveedores")

    # ---------------- FORMULARIO ----------------
    st.subheader("➕ Registrar Evaluación")

    with st.form("form_proveedor", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            numero = st.number_input("N°", min_value=1, step=1)
            mes = st.selectbox("MES", [
                "Enero","Febrero","Marzo","Abril","Mayo","Junio",
                "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
            ])
            ruc = st.text_input("RUC")
            proveedor = st.text_input("PROVEEDOR")

        with col2:
            rubro = st.text_input("RUBRO")
            puntaje = st.number_input("PUNTAJE (0 a 5)", min_value=0.0, max_value=5.0, step=0.1)
            criticidad = st.selectbox("CRITICIDAD", ["CRITICO", "NO CRITICO"])
            estado_prov = st.selectbox("ESTADO PROV", ["ACTIVO", "INACTIVO"])

        with col3:
            fecha = st.date_input("FECHA", value=datetime.today())
            reevaluacion = st.date_input("REEVALUACION")

        if st.form_submit_button("Guardar"):

            if ruc == "" or proveedor == "":
                st.error("⚠️ RUC y PROVEEDOR son obligatorios")
            else:
                if puntaje >= 4:
                    estatus = "APROBADO"
                    calificacion = "BUENO"
                elif puntaje >= 3:
                    estatus = "OBSERVADO"
                    calificacion = "REGULAR"
                else:
                    estatus = "NO APROBADO"
                    calificacion = "DEFICIENTE"

                estado = "VIGENTE" if estado_prov == "ACTIVO" else "NO VIGENTE"

                nuevo = pd.DataFrame([{
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

                df = pd.concat([df, nuevo], ignore_index=True)
                df.to_csv(FILE_NAME, index=False)
                st.success("✅ Registro guardado")

    # ---------------- TABLA ----------------
    st.subheader("📋 Base de Datos")

    if not df.empty:
        edited_df = st.data_editor(df, use_container_width=True)

        if st.button("💾 Guardar cambios"):
            edited_df.to_csv(FILE_NAME, index=False)
            st.success("Cambios guardados")

    # ---------------- ELIMINACIÓN ----------------
    st.subheader("🗑️ Eliminar registros")

    if not df.empty:
        seleccion = st.multiselect(
            "Selecciona registros",
            options=df.index,
            format_func=lambda x: f"{df.loc[x,'PROVEEDOR']} - {df.loc[x,'RUC']}"
        )

        if st.button("Eliminar seleccionados"):
            if seleccion:
                df = df.drop(seleccion).reset_index(drop=True)
                df.to_csv(FILE_NAME, index=False)
                st.success("Registros eliminados")

        if st.checkbox("Confirmar borrado total"):
            if st.button("🧨 Borrar todo"):
                df = df.iloc[0:0]
                df.to_csv(FILE_NAME, index=False)
                st.error("Base eliminada")

    # ---------------- INDICADOR ----------------
    st.subheader("📈 Indicador")

    df_criticos = df[df["CRITICIDAD"] == "CRITICO"]

    total = len(df_criticos)
    aprobados = len(df_criticos[df_criticos["ESTATUS"] == "APROBADO"])

    indicador = (aprobados / total) * 100 if total > 0 else 0

    st.metric("Indicador (%)", f"{indicador:.2f}%")

    if indicador >= 95:
        st.success("✅ Meta cumplida")
    else:
        st.error("❌ Meta no cumplida")

# ============================================================
# ============== MODULO 2: SATISFACCION CLIENTE ===============
# ============================================================
elif menu == "Satisfacción del Cliente":

    FILE_PATH = "satisfaccion_cliente.xlsx"
    SHEET_NAME = "SIG (1)"

    st.title("😊 Satisfacción del Cliente")

    # -------- FUNCIONES --------
    def cargar_datos():
        columnas = [
            "MES","FECHA DE EVALUACION","CLIENTE EVALUADO",
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

    # -------- FORMULARIO --------
    st.subheader("➕ Registrar evaluación")

    with st.form("form_cliente"):
        col1, col2, col3 = st.columns(3)

        mes = col1.selectbox("MES", [
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
        ])
        fecha = col2.date_input("FECHA")
        cliente = col3.text_input("CLIENTE")

        st.markdown("### Evaluación (1-10)")
        preguntas = {}
        cols = st.columns(5)

        for i in range(10):
            with cols[i % 5]:
                preguntas[f"P{i+1}"] = st.number_input(
                    f"P{i+1}", 1.0, 10.0, step=0.1, key=f"p{i}"
                )

        if st.form_submit_button("Guardar"):
            nueva = {"MES": mes, "FECHA DE EVALUACION": fecha, "CLIENTE EVALUADO": cliente}
            nueva.update(preguntas)

            df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
            guardar_datos(df)
            st.success("Registro guardado")

    # -------- KPI --------
    st.subheader("📈 Indicador")

    if not df.empty:
        respuestas = df[[f"P{i}" for i in range(1,11)]].values.flatten()
        respuestas = [r for r in respuestas if pd.notnull(r)]

        positivas = len([r for r in respuestas if r >= 8])
        porcentaje = (positivas / len(respuestas)) * 100 if respuestas else 0

        st.metric("% Satisfacción", f"{porcentaje:.2f}%")

        if porcentaje >= 90:
            st.success("Excelente")
        elif porcentaje >= 75:
            st.warning("Aceptable")
        else:
            st.error("Crítico")

    # -------- HISTORIAL --------
    st.subheader("📋 Historial")
    if not df.empty:
        st.dataframe(df, use_container_width=True)

    # -------- ELIMINAR --------
    st.subheader("🗑️ Eliminar")

    if not df.empty:
        idx = st.number_input("Índice", 0, len(df)-1)

        if st.checkbox("Confirmar"):
            if st.button("Eliminar"):
                df = df.drop(idx).reset_index(drop=True)
                guardar_datos(df)
                st.success("Eliminado")

    # -------- GRAFICO --------
    if not df.empty:
        df["Promedio"] = df[[f"P{i}" for i in range(1,11)]].mean(axis=1)
        st.subheader("📊 Tendencia")
        st.line_chart(df["Promedio"])
