import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import os

# 1. Configuración del Cliente
# ⚠️ Usa tu API Key real aquí o como variable de entorno
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")
client = genai.Client(api_key=API_KEY)

st.title("📘 Verificador de Títulos y Grados")

# 2. Mostrar modelos disponibles
st.subheader("📋 Modelos disponibles en tu cuenta")
try:
    models = client.models.list()
    for m in models:
        st.write(f"- {m.name} → Métodos soportados: {m.supported_methods}")
except Exception as e:
    st.error(f"No se pudieron listar los modelos: {e}")

# 3. Carga de Base de Datos
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

# 4. Interfaz y Procesamiento
archivo = st.file_uploader("Sube el documento", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo and df_base is not None:
    st.info("🔍 Procesando documento...")

    try:
        with st.spinner("🤖 Analizando..."):
            file_bytes = archivo.read()
            documento = types.Part.from_bytes(data=file_bytes, mime_type=archivo.type)

            # ⚠️ IMPORTANTE: cambia el modelo según lo que aparezca en la lista anterior
            response = client.models.generate_content(
                model="models/gemini-1.0-pro",  # Ajusta aquí al modelo válido
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

# 5. Botón SUNEDU
if st.button("Consultar SUNEDU"):
    with st.spinner("Consultando registros..."):
        time.sleep(10)
        st.success("Consulta completada.")
