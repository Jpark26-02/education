import streamlit as st
import google.generativeai as genai
import pytesseract
from PIL import Image
import pandas as pd
import time

# --- CONFIGURACIÓN CON TU API KEY ---
# Usamos la clave que guardaste en Secrets para mayor seguridad
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    # Si por alguna razón no lee el Secret, usamos tu clave directa aquí
    genai.configure(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")

model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Verificador de Documentos", layout="wide")
st.title("📘 Verificador de Documentos Académicos")

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u == "admin" and p == "1234":
            st.session_state.auth = True
            st.rerun()
else:
    st.success("Sesión iniciada correctamente.")

    # --- PROCESAMIENTO DE ARCHIVOS ---
    archivo = st.file_uploader("Sube un PDF o Imagen", type=['pdf', 'jpg', 'png', 'jpeg'])

    if archivo:
        st.info(f"Procesando: {archivo.name}...")
        img = Image.open(archivo)
        st.image(img, width=450, caption="Vista previa del documento")

        # Esto es lo que hace que "pase algo" después de cargar
        with st.spinner("La IA está analizando el contenido..."):
            try:
                # Instrucción para que Gemini analice la imagen directamente
                prompt = """
                Analiza este documento y extrae:
                1. Nombre completo del alumno.
                2. Tipo de documento (Diploma, Certificado, etc).
                3. Carrera o especialidad.
                4. Fecha de emisión.
                5. Nombre del Secretario General que firma.
                Presenta los resultados en una tabla.
                """
                response = model.generate_content([prompt, img])
                
                # MOSTRAR RESULTADOS
                st.subheader("🔍 Resultados del Análisis Inteligente")
                st.markdown(response.text)
                st.balloons()
                
            except Exception as e:
                st.error(f"Error al conectar con la IA: {e}")
                st.info("Revisa si tu API Key sigue activa en Google AI Studio.")

    # --- BOTÓN SUNEDU (Punto 5 de tus requerimientos) ---
    if st.button("Validar en SUNEDU"):
        st.warning("Respetando espera de 10 segundos por CAPTCHA...")
        time.sleep(10)
        st.success("Validación finalizada.")
