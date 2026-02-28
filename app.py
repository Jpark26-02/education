import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la Llave
# Usamos tu clave directa para asegurar que no falle nada
API_KEY = "AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Interfaz que ya tienes funcionando
st.title("📘 Verificador de Documentos")
st.success("Sistema Conectado con Gemini IA")

# 3. Lógica de Subida de Archivos
archivo = st.file_uploader("Sube una IMAGEN del documento (JPG o PNG)", type=['jpg', 'png', 'jpeg'])

if archivo:
    st.write("✅ Archivo recibido. Analizando con Inteligencia Artificial...")
    try:
        # Abrimos la imagen para que la IA la vea
        img = Image.open(archivo)
        st.image(img, width=400, caption="Documento cargado")
        
        # Llamada a Gemini para extraer los datos
        with st.spinner("🤖 La IA está leyendo el documento..."):
            # Este es el "comando" para la IA
            prompt = """
            Analiza esta imagen de un documento académico y extrae la siguiente información:
            - Nombre completo del graduado
            - Carrera o especialidad
            - Fecha de emisión
            - Nombre de la autoridad o secretario que firma
            Presentalo en una lista clara.
            """
            response = model.generate_content([prompt, img])
            
            # MOSTRAR RESULTADOS FINALES
            st.subheader("🔍 Datos Extraídos del Documento:")
            st.info(response.text)
            st.balloons() # Celebramos que funcionó
            
    except Exception as e:
        st.error(f"Ocurrió un error al procesar la imagen: {e}")
