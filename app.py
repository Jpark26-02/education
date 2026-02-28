import streamlit as st
import google.generativeai as genai
import time

# 1. Configuración de la IA con tu clave
API_KEY = "AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774"
genai.configure(api_key=API_KEY)

# Usamos el modelo 1.5-flash que es el especialista en PDFs
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📘 Verificador de Documentos PDF")
st.success("Sistema Conectado con Gemini IA (Modo PDF Activo)")

# 2. Selector de archivos configurado para PDF e Imágenes
archivo = st.file_uploader("Sube el PDF del diploma o certificado", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo:
    st.write(f"✅ Archivo '{archivo.name}' recibido. Analizando contenido...")
    
    try:
        with st.spinner("🤖 La IA está procesando el PDF..."):
            # Le pasamos el archivo directamente a Gemini 1.5
            prompt = """
            Analiza este documento académico (PDF o Imagen). 
            Extrae y presenta en una lista:
            - Nombre completo del graduado
            - Carrera o especialidad
            - Fecha de emisión
            - Secretario General o autoridad que firma
            """
            
            # Procesamiento directo del archivo
            # Nota: Gemini 1.5 puede leer bytes de archivos directamente
            bytes_data = archivo.read()
            contenido = [
                {"mime_type": archivo.type, "data": bytes_data},
                prompt
            ]
            
            response = model.generate_content(contenido)
            
            # 3. Mostrar Resultados
            st.subheader("🔍 Datos Extraídos del PDF:")
            st.info(response.text)
            st.balloons()
            
    except Exception as e:
        st.error(f"Hubo un problema al leer el PDF: {e}")
        st.info("Tip: Si el error persiste, intenta subir una versión en imagen (JPG) para descartar errores de formato.")

# Botón de validación según tu requerimiento Punto 5
if st.button("Validar Firma en Base de Datos"):
    with st.spinner("Validando fechas de gestión..."):
        time.sleep(2)
        st.warning("Función de comparación con 'secretarios.csv' lista para configurar.")
