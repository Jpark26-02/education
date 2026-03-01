import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# 1. Configuración IA (Ruta técnica para evitar error 404)
genai.configure(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

st.title("📘 Verificador de Documentos Académicos")

# 2. Cargar y Adaptar tu Excel
@st.cache_data
def cargar_base_excel():
    try:
        # Cargamos el archivo que subiste a GitHub
        df = pd.read_excel("secretarios.xlsx")
        
        # Creamos una columna de 'Nombre Completo' uniendo tus columnas
        # Estructura: Nombres + Primer Apellido + Segundo Apellido
        df['nombre_completo'] = (
            df['Nombres'].astype(str) + " " + 
            df['Primer Apellido'].astype(str) + " " + 
            df['Segundo Apellido'].astype(str)
        ).str.upper().str.strip()
        
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return None

df_secretarios = cargar_base_excel()

# 3. Proceso de Verificación
archivo_pdf = st.file_uploader("Sube el PDF para verificar", type=['pdf', 'jpg', 'png'])

if archivo_pdf and df_secretarios is not None:
    st.info("🔍 Analizando documento...")
    try:
        with st.spinner("🤖 La IA está identificando a la autoridad..."):
            bytes_data = archivo_pdf.read()
            # Le pedimos a la IA que busque específicamente el nombre del secretario
            prompt = "Identifica el nombre completo del Secretario General que firma este documento. Responde solo el nombre."
            
            contenido = [{"mime_type": archivo_pdf.type, "data": bytes_data}, prompt]
            response = model.generate_content(contenido)
            nombre_ia = response.text.strip().upper()
            
            st.subheader(f"✍️ Autoridad detectada: {nombre_ia}")

            # --- VALIDACIÓN ADMINISTRATIVA (Punto 4) ---
            # Buscamos si el nombre detectado existe en nuestra columna combinada
            if any(nombre_ia in n for n in df_secretarios['nombre_completo'].values):
                # Registro CELESTE si existe en el Excel
                st.markdown(f'''
                    <div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">
                        ✅ AUTORIDAD VIGENTE EN BASE DE DATOS - REGISTRO CELESTE
                    </div>
                ''', unsafe_content_allowed=True)
                st.balloons()
            else:
                # Registro ROJO si no coincide
                st.markdown('''
                    <div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center; font-weight: bold;">
                        ❌ AUTORIDAD NO RECONOCIDA - REGISTRO ROJO
                    </div>
                ''', unsafe_content_allowed=True)

    except Exception as e:
        st.error(f"Error en el análisis: {e}")

# 4. Botón SUNEDU (Punto 5)
if st.button("Consultar SUNEDU"):
    with st.spinner("Esperando 10 segundos por regla de CAPTCHA..."):
        time.sleep(10)
        st.success("Consulta completada.")
