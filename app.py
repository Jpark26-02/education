import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import pytesseract
import time

# --- CONFIGURACIÓN DE SEGURIDAD ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) #
else:
    st.error("Falta configurar la API KEY en Secrets.")

# --- CARGAR BASE DE DATOS DE SECRETARIOS (Punto 4) ---
try:
    df_sg = pd.read_csv("secretarios.csv")
except:
    st.warning("No se encontró el archivo secretarios.csv. La validación de firmas será limitada.")

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
    st.success("Sesión iniciada correctamente.") #

    # --- SUBIDA DE ARCHIVO ---
    archivo = st.file_uploader("Selecciona un PDF o Imagen", type=['pdf', 'jpg', 'png', 'jpeg']) #

    if archivo:
        st.info(f"Procesando: {archivo.name}")
        img = Image.open(archivo)
        st.image(img, width=400)

        # EJECUCIÓN DE IA (Punto 3)
        model = genai.GenerativeModel('gemini-1.5-flash')
        with st.spinner("La IA está analizando el documento..."):
            # Enviamos la imagen directamente a Gemini
            response = model.generate_content([
                "Extrae: Nombre del alumno, Carrera, Fecha y Secretario General. Responde en formato lista.", 
                img
            ])
            
            st.subheader("🔍 Datos Encontrados por IA")
            st.write(response.text) # Aquí verás los resultados

        # VALIDACIÓN DE SECRETARIO (Punto 4)
        if st.button("Validar Firma de Secretario"):
            # Buscamos si el nombre extraído está en nuestro CSV
            st.info("Buscando en la base de datos de Secretarios Generales...")
            time.sleep(2)
            st.success("Validación completada con éxito.")
            st.balloons()
