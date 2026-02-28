import streamlit as st
import google.generativeai as genai
import pytesseract
from PIL import Image
import pandas as pd

# Configuración de la IA
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📘 Verificador de Documentos")

# Si el usuario sube un archivo
archivo = st.file_uploader("Sube tu documento", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo:
    st.info("Procesando documento...")
    img = Image.open(archivo)
    st.image(img, width=400) # Muestra lo que subiste

    # ESTO ES LO QUE FALTA EN TU CÓDIGO: La orden de analizar
    with st.spinner("La IA está leyendo el documento..."):
        try:
            # Enviamos la imagen a Gemini para que extraiga los datos
            response = model.generate_content(["Extrae el nombre del alumno, carrera y fecha de este documento.", img])
            st.subheader("🔍 Datos Extraídos:")
            st.write(response.text) # Aquí aparecerán los resultados
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")
