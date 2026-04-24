def importar_excel(df_actual, columnas_esperadas, guardar_func):
    st.subheader("📥 Importar datos desde Excel")

    archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

    if archivo is not None:
        try:
            df_nuevo = pd.read_excel(archivo)

            # Validar columnas
            columnas_archivo = set(df_nuevo.columns)
            columnas_requeridas = set(columnas_esperadas)

            if not columnas_requeridas.issubset(columnas_archivo):
                st.error("❌ El archivo no tiene la estructura correcta")
                st.write("Columnas esperadas:", columnas_esperadas)
                st.write("Columnas encontradas:", list(df_nuevo.columns))
                return df_actual

            # Concatenar datos
            df_final = pd.concat([df_actual, df_nuevo], ignore_index=True)

            guardar_func(df_final)

            st.success(f"✅ {len(df_nuevo)} registros importados correctamente")

            return df_final

        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

    return df_actual
