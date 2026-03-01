import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time

# 1. Usamos tu clave que ya tenemos configurada
client = genai.Client(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")

st.title("📘 Verificador de Títulos y Grados")

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

archivo = st.file_uploader("Sube el documento", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo and df_base is not None:
    st.info("🔍 Intento de conexión con Gemini 1.0 Pro...")
    
    try:
        with st.spinner("🤖 Procesando..."):
            file_bytes = archivo.read()
            # Empaquetado simple
            documento = types.Part.from_bytes(data=file_bytes, mime_type=archivo.type)
            
            # CAMBIO CLAVE: Modelo 1.0 (El que viene por defecto en todas las llaves)
            response = client.models.generate_content(
                model="gemini-1.0-pro-vision-latest", 
                contents=[
                    "Dime el nombre del secretario que firma este documento.",
                    documento
                ]
            )
            
            nombre_ia = response.text.strip().upper()
            st.subheader(f"✍️ Detectado: {nombre_ia}")

            # Validación de color
            match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=False)]

            if not match.empty:
                st.markdown(f'<div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">✅ REGISTRO CELESTE: {match["Universidad"].values[0]}</div>', unsafe_content_allowed=True)
                st.balloons()
            else:
                st.markdown('<div style="
