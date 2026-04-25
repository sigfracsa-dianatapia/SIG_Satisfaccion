import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="SIG Integral", layout="wide")

# ============================================================
# 🔧 FUNCIONES BASE
# ============================================================
def importar_excel(df, columnas, guardar):
    archivo = st.file_uploader("📥 Importar Excel", type=["xlsx"])
    if archivo:
        nuevo = pd.read_excel(archivo)
        if set(columnas).issubset(set(nuevo.columns)):
            df = pd.concat([df, nuevo], ignore_index=True)
            guardar(df)
            st.success("Datos importados")
        else:
            st.error("Estructura incorrecta")
    return df

def eliminar_filas(df, guardar):
    if not df.empty:
        sel = st.multiselect("Eliminar filas", df.index)
        if st.button("Eliminar"):
            df = df.drop(sel)
            guardar(df)
    return df

def dashboard_simple(df, columna):
    if not df.empty and columna in df.columns:
        st.line_chart(df[columna])

# ============================================================
# 📌 MENÚ
# ============================================================
menu = st.sidebar.selectbox("Módulos SIG", [
    "Proveedores","Satisfacción","Programación",
    "Combustible","Combustible PP","OTIF","SST1","SST2"
])

# ============================================================
# 1️⃣ PROVEEDORES
# ============================================================
if menu == "Proveedores":

    FILE="prov.csv"
    cols=["N°","MES","RUC","PROVEEDOR","RUBRO","PUNTAJE","ESTATUS","CALIFICACION","FECHA","REEVALUACION","ESTADO","CRITICIDAD","ESTADO PROV"]

    if not os.path.exists(FILE):
        pd.DataFrame(columns=cols).to_csv(FILE,index=False)

    df=pd.read_csv(FILE)
    guardar=lambda x:x.to_csv(FILE,index=False)

    st.title("📊 Proveedores")

    df=importar_excel(df,cols,guardar)

    with st.form("f"):
        prov=st.text_input("Proveedor")
        punt=st.number_input("Puntaje",0.0,5.0)
        if st.form_submit_button("Guardar"):
            df=pd.concat([df,pd.DataFrame([{
                "N°":len(df)+1,"PROVEEDOR":prov,"PUNTAJE":punt,
                "ESTATUS":"APROBADO" if punt>=4 else "NO"
            }])])
            guardar(df)

    crit=df[df["CRITICIDAD"]=="CRITICO"]
    kpi=(len(crit[crit["ESTATUS"]=="APROBADO"])/len(crit))*100 if len(crit)>0 else 0
    st.metric("% Evaluación",round(kpi,2))

    st.subheader("📊 Dashboard")
    dashboard_simple(df,"PUNTAJE")

    st.dataframe(df)
    df=eliminar_filas(df,guardar)

# ============================================================
# 2️⃣ SATISFACCIÓN
# ============================================================
elif menu=="Satisfacción":

    FILE="cli.xlsx"
    cols=["MES","FECHA","CLIENTE"]+[f"P{i}" for i in range(1,11)]

    df=pd.read_excel(FILE) if os.path.exists(FILE) else pd.DataFrame(columns=cols)
    guardar=lambda x:x.to_excel(FILE,index=False)

    st.title("😊 Satisfacción")

    df=importar_excel(df,cols,guardar)

    with st.form("f2"):
        cliente=st.text_input("Cliente")
        preguntas={f"P{i}":st.number_input(f"P{i}",1.0,10.0) for i in range(1,11)}
        if st.form_submit_button("Guardar"):
            nuevo={"CLIENTE":cliente}
            nuevo.update(preguntas)
            df=pd.concat([df,pd.DataFrame([nuevo])])
            guardar(df)

    vals=df[[f"P{i}" for i in range(1,11)]].values.flatten() if not df.empty else []
    vals=[v for v in vals if pd.notnull(v)]
    kpi=(len([v for v in vals if v>=8])/len(vals))*100 if vals else 0
    st.metric("% Satisfacción",round(kpi,2))

    st.subheader("📊 Dashboard")
    if not df.empty:
        df["Prom"]=df[[f"P{i}" for i in range(1,11)]].mean(axis=1)
        st.line_chart(df["Prom"])

    st.dataframe(df)
    df=eliminar_filas(df,guardar)

# ============================================================
# 3️⃣ PROGRAMACIÓN
# ============================================================
elif menu=="Programación":

    FILE="prog.xlsx"
    cols=["N°","MES","CANTIDAD","CUMPLIDOS","NO CUMPLIDOS","%"]

    df=pd.read_excel(FILE) if os.path.exists(FILE) else pd.DataFrame(columns=cols)
    guardar=lambda x:x.to_excel(FILE,index=False)

    st.title("📊 Programación")

    df=importar_excel(df,cols,guardar)

    with st.form("f3"):
        total=st.number_input("Total",0)
        cumpl=st.number_input("Cumplidos",0)
        if st.form_submit_button("Guardar"):
            df=pd.concat([df,pd.DataFrame([{
                "N°":len(df)+1,
                "CANTIDAD":total,
                "CUMPLIDOS":cumpl,
                "%":(cumpl/total)*100 if total>0 else 0
            }])])
            guardar(df)

    kpi=(df["CUMPLIDOS"].sum()/df["CANTIDAD"].sum())*100 if not df.empty else 0
    st.metric("% Cumplimiento",round(kpi,2))

    st.subheader("📊 Dashboard")
    dashboard_simple(df,"%")

    st.dataframe(df)
    df=eliminar_filas(df,guardar)

# ============================================================
# 4️⃣ COMBUSTIBLE (SIMPLIFICADO)
# ============================================================
elif menu=="Combustible":

    FILE="comb.xlsx"
    cols=["TOTAL","CANTIDAD12"]

    df=pd.read_excel(FILE) if os.path.exists(FILE) else pd.DataFrame(columns=cols)
    guardar=lambda x:x.to_excel(FILE,index=False)

    st.title("⛽ Variación Combustible")

    df=importar_excel(df,cols,guardar)

    kpi=(df["TOTAL"].sum()/df["CANTIDAD12"].sum())*100 if not df.empty else 0
    st.metric("% Variación",round(kpi,2))

    dashboard_simple(df,"TOTAL")
    st.dataframe(df)
    df=eliminar_filas(df,guardar)

# ============================================================
# 5️⃣ OTIF
# ============================================================
elif menu=="OTIF":

    FILE="otif.xlsx"
    cols=["VIAJES","SIN MERMA"]

    df=pd.read_excel(FILE) if os.path.exists(FILE) else pd.DataFrame(columns=cols)
    guardar=lambda x:x.to_excel(FILE,index=False)

    st.title("🚚 OTIF")

    df=importar_excel(df,cols,guardar)

    kpi=(df["SIN MERMA"].sum()/df["VIAJES"].sum())*100 if not df.empty else 0
    st.metric("% OTIF",round(kpi,2))

    dashboard_simple(df,"SIN MERMA")
    st.dataframe(df)
    df=eliminar_filas(df,guardar)

# ============================================================
# 6️⃣ SST (FRECUENCIA)
# ============================================================
elif menu=="SST1":

    FILE="sst1.xlsx"
    cols=["TA","HHT"]

    df=pd.read_excel(FILE) if os.path.exists(FILE) else pd.DataFrame(columns=cols)
    guardar=lambda x:x.to_excel(FILE,index=False)

    st.title("🦺 Índice Frecuencia")

    df=importar_excel(df,cols,guardar)

    kpi=(df["TA"].sum()/df["HHT"].sum())*100 if not df.empty else 0
    st.metric("Frecuencia",round(kpi,2))

    dashboard_simple(df,"TA")
    st.dataframe(df)
    df=eliminar_filas(df,guardar)

# ============================================================
# 7️⃣ SST (REPORTE)
# ============================================================
elif menu=="SST2":

    FILE="sst2.xlsx"
    cols=["CERRADOS","TOTAL"]

    df=pd.read_excel(FILE) if os.path.exists(FILE) else pd.DataFrame(columns=cols)
    guardar=lambda x:x.to_excel(FILE,index=False)

    st.title("📊 Reporte Accidentes")

    df=importar_excel(df,cols,guardar)

    kpi=(df["CERRADOS"].sum()/df["TOTAL"].sum())*100 if not df.empty else 0
    st.metric("% Cierre",round(kpi,2))

    dashboard_simple(df,"CERRADOS")
    st.dataframe(df)
    df=eliminar_filas(df,guardar)
