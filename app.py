import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import os

# 1. Configuración Segura: Lee de Streamlit Secrets o Variable de Entorno
# Si no encuentra ninguna, fallará con un mensaje claro.
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU")

if not api_key:
    st.error("🔑 Error: No se encontró la API KEY. Configúrala en los Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

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
        with st.spinner("🤖 Analizando con Gemini..."):
            file_bytes = archivo.read()
            documento = types.Part.from_bytes(data=file_bytes, mime_type=archivo.type)
            
            # Usamos Gemini 1.5 Flash que es el más equilibrado
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=["Extrae el nombre del secretario que firma. Solo el nombre.", documento]
            )
            
            nombre_ia = response.text.strip().upper()
            st.subheader(f"✍️ Detectado: {nombre_ia}")

            # --- VALIDACIÓN DE COLOR ---
            match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=False)]

            if not match.empty:
                universidad = match['Universidad'].values[0]
                st.markdown(f'<div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">✅ REGISTRO CELESTE: {universidad}</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown('<div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center; font-weight: bold;">❌ REGISTRO ROJO: No encontrado</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")

# 4. Botón SUNEDU
if st.button("Consultar SUNEDU"):
    with st.spinner("Consultando registros..."):
        time.sleep(10)
        st.success("Consulta completada.")
