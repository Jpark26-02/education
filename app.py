import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# 1. Configuración IA (Ruta corregida para evitar error 404)
genai.configure(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

st.title("📘 Verificador con Base de Datos Excel")

# 2. Cargar tu Base de Datos de Excel (Punto 4)
@st.cache_data
def cargar_base():
    try:
        # Intenta leer el archivo que subiste a GitHub
        df = pd.read_excel("secretarios.xlsx")
        # Convertimos a mayúsculas para que la comparación sea exacta
        df['nombre'] = df['nombre'].astype(str).str.upper().str.strip()
        return df
    except Exception as e:
        st.error(f"No se pudo leer 'secretarios.xlsx'. Error: {e}")
        return pd.DataFrame(columns=['nombre'])

df_secretarios = cargar_base()

# 3. Procesamiento de Documentos
archivo_pdf = st.file_uploader("Sube el PDF para verificar", type=['pdf', 'jpg', 'png'])

if archivo_pdf:
    st.info(f"📄 Analizando: {archivo_pdf.name}")
    try:
        with st.spinner("🤖 Gemini extrayendo datos..."):
            bytes_data = archivo_pdf.read()
            prompt = "Extrae el NOMBRE del Secretario General que firma este documento. Responde solo el nombre."
            
            contenido = [{"mime_type": archivo_pdf.type, "data": bytes_data}, prompt]
            response = model.generate_content(contenido)
            nombre_extraido = response.text.strip().upper()
            
            st.subheader(f"✍️ Secretario detectado: {nombre_extraido}")

            # --- VALIDACIÓN CONTRA TU EXCEL (Punto 4) ---
            if nombre_extraido in df_secretarios['nombre'].values:
                # Fondo CELESTE
                st.markdown(f'''
                    <div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">
                        ✅ AUTORIDAD ENCONTRADA EN EXCEL - REGISTRO CELESTE
                    </div>
                ''', unsafe_content_allowed=True)
                st.balloons()
            else:
                # Fondo ROJO
                st.markdown('''
                    <div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center; font-weight: bold;">
                        ❌ AUTORIDAD NO REGISTRADA - REGISTRO ROJO
                    </div>
                ''', unsafe_content_allowed=True)

    except Exception as e:
        st.error(f"Error técnico: {e}")

# 4. Regla SUNEDU (Punto 5)
if st.button("Consultar SUNEDU"):
    with st.spinner("Esperando 10 segundos..."):
        time.sleep(10)
        st.success("Consulta completada.")
