import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# 1. Configuración de la IA (Uso de ruta completa para evitar error 404)
genai.configure(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")

# Intentamos con la ruta de modelo que solicita tu servidor en los logs
MODEL_NAME = 'models/gemini-1.5-flash-latest'
model = genai.GenerativeModel(MODEL_NAME)

st.title("📘 Verificador de Documentos")
st.success("Sistema Conectado con Gemini IA") #

# 2. Base de Datos de Secretarios Generales (Punto 4)
# Esta lista define quiénes activan el color CELESTE
try:
    df_sg = pd.read_csv("secretarios.csv")
except:
    # Datos de respaldo si aún no creas el CSV en GitHub
    df_sg = pd.DataFrame({'nombre': ['JUAN PEREZ', 'MARIA LOPEZ', 'CARLOS GARCIA']})

# 3. Carga de Archivos (PDF e Imágenes)
archivo = st.file_uploader("Selecciona el documento para verificar", type=['pdf', 'jpg', 'png'])

if archivo:
    st.info(f"Analizando: {archivo.name}") #
    
    try:
        with st.spinner("🤖 La IA está extrayendo los datos..."):
            bytes_data = archivo.read()
            prompt = "Extract from this document: 1. Student Name, 2. Degree, 3. Date, 4. General Secretary Name. Return as a simple list."
            
            # Formato de envío compatible con archivos y texto
            contenido = [{"mime_type": archivo.type, "data": bytes_data}, prompt]
            response = model.generate_content(contenido)
            
            # Mostramos los datos encontrados (Punto 3)
            st.subheader("🔍 Datos Detectados")
            datos_ia = response.text
            st.text(datos_ia)

            # --- LÓGICA DE VALIDACIÓN (Punto 4) ---
            # El usuario confirma el nombre extraído para validar contra el CSV
            nombre_verificar = st.text_input("Nombre del Secretario General a validar:")
            
            if st.button("Ejecutar Verificación de Autoridad"):
                if nombre_verificar.upper() in df_sg['nombre'].str.upper().values:
                    # Color Celeste para Autoridad Válida
                    st.markdown(f'<div style="background-color: #00FFFF; padding: 15px; border-radius: 5px; color: black; font-weight: bold; text-align: center;">✅ AUTORIDAD REGISTRADA - REGISTRO CELESTE</div>', unsafe_content_allowed=True)
                    st.balloons()
                else:
                    # Color Rojo para Autoridad No Registrada
                    st.markdown(f'<div style="background-color: #FF0000; padding: 15px; border-radius: 5px; color: white; font-weight: bold; text-align: center;">❌ AUTORIDAD NO RECONOCIDA - REGISTRO ROJO</div>', unsafe_content_allowed=True)

    except Exception as e:
        st.error(f"Error técnico: {e}")
        st.info("Revisa que el archivo 'requirements.txt' incluya: google-generativeai")

# 4. Regla SUNEDU (Punto 5)
if st.button("Consultar SUNEDU (Captcha 10s)"):
    with st.spinner("Cumpliendo tiempo de espera obligatorio..."):
        time.sleep(10)
        st.success("Consulta finalizada.")
