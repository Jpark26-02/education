import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la Llave (Directa para evitar errores de Secrets por ahora)
API_KEY = "AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Interfaz Básica
st.title("📘 Verificador de Documentos")

# Forzamos que la sesión esté iniciada para saltar errores de login
st.session_state['auth'] = True 

if st.session_state['auth']:
    st.success("Sistema Conectado con Gemini IA")
    
    # Subida de archivo
    archivo = st.file_uploader("Sube una IMAGEN del documento (JPG o PNG)", type=['jpg', 'png', 'jpeg'])

    if archivo:
        st.write("✅ Archivo recibido. Analizando...")
        try:
            # Abrir la imagen
            img = Image.open(archivo)
            st.image(img, width=300, caption="Documento cargado")
            
            # Llamada a la IA
            with st.spinner("Leyendo con IA..."):
                prompt = "Analiza esta imagen. Dime el NOMBRE del graduado y la CARRERA que aparece."
                response = model.generate_content([prompt, img])
                
                st.subheader("🔍 Datos Extraídos:")
                st.info(response.text)
                st.balloons()
                
        except Exception as e:
            st.error(f"Error al procesar: {e}")
