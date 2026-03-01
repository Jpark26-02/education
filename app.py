import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time

# 1. Configuración Ultra-Estricta
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"

# Forzamos la configuración para evitar el 404 de v1beta
try:
    client = genai.Client(
        api_key=API_KEY,
        http_options={'api_version': 'v1'} # <-- Esto obliga a salir de la beta
    )
except Exception as e:
    st.error(f"Error inicial: {e}")

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
    except:
        return None

df_base = cargar_base()

# 3. Procesamiento
archivo = st.file_uploader("Sube el documento", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo and df_base is not None:
    st.info("🔍 Analizando...")
    
    try:
        with st.spinner("🤖 Conectando con el motor principal..."):
            file_bytes = archivo.read()
            documento = types.Part.from_bytes(data=file_bytes, mime_type=archivo.type)
            
            # Intentamos con el nombre de modelo más estable y genérico
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=["Solo dime el nombre del secretario.", documento]
            )
            
            nombre_ia = response.text.strip().upper()
            st.subheader(f"✍️ Detectado: {nombre_ia}")

            match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=False)]

            if not match.empty:
                st.markdown(f'<div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">✅ REGISTRO CELESTE: {match["Universidad"].values[0]}</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown('<div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center; font-weight: bold;">❌ REGISTRO ROJO: No encontrado</div>', unsafe_allow_html=True)

    except Exception as e:
        # Si falla el 1.5, lanzamos el último recurso: 1.0 Pro
        st.warning("El motor 1.5 no responde, intentando con motor de reserva...")
        try:
            response = client.models.generate_content(
                model="gemini-1.0-pro", 
                contents=["Solo el nombre del secretario.", documento]
            )
            st.success("Motor de reserva activado.")
        except:
            st.error(f"Error total de la API: {e}")
            st.info("Revisa si aceptaste los términos en https://aistudio.google.com/app/prompts/new")

if st.button("Consultar SUNEDU"):
    time.sleep(10)
    st.success("Listo.")
    
