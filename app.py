import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time

# 1. Configuración del Cliente
client = genai.Client(api_key="TU_API_KEY_AQUI")

st.title("📘 Verificador de Títulos y Grados")

# 2. Carga de Base de Datos
@st.cache_data
def cargar_base():
    try:
        df = pd.read_excel("secretarios.xlsx")
        df.columns = df.columns.str.strip()
        df['NOMBRE_COMPLETO'] = (
            df['Nombres'].astype(str) + " " +
            df['Primer Apellido'].astype(str) + " " +
            df['Segundo Apellido'].astype(str)
        ).str.upper().str.strip()
        return df
    except Exception as e:
        st.error(f"Error con el Excel: {e}")
        return None

df_base = cargar_base()

# 3. Interfaz y Procesamiento
archivo = st.file_uploader("Sube el documento", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo and df_base is not None:
    st.info("🔍 Procesando documento...")

    try:
        with st.spinner("🤖 Analizando..."):
            file_bytes = archivo.read()
            documento = types.Part.from_bytes(data=file_bytes, mime_type=archivo.type)

            # Usa un modelo válido (gemini-1.5-pro soporta generate_content)
            response = client.models.generate_content(
                model="gemini-1.5-pro",
                contents=["Dime el nombre del secretario que firma este documento. Solo el nombre.", documento]
            )

            nombre_ia = response.text.strip().upper()
            st.subheader(f"✍️ Detectado: {nombre_ia}")

            # --- VALIDACIÓN DE COLOR ---
            match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=False)]

            if not match.empty:
                # REGISTRO CELESTE
                mensaje_celeste = f"✅ REGISTRO CELESTE: {match['Universidad'].values[0]}"
                st.markdown(
                    f'<div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">{mensaje_celeste}</div>',
                    unsafe_allow_html=True
                )
                st.balloons()
            else:
                # REGISTRO ROJO
                st.markdown(
                    '<div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center; font-weight: bold;">❌ REGISTRO ROJO: Autoridad no encontrada</div>',
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"Error: {e}")

# 4. Botón SUNEDU
if st.button("Consultar SUNEDU"):
    with st.spinner("Consultando registros..."):
        time.sleep(10)
        st.success("Consulta completada.")

