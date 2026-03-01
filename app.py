import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# 1. Configuración de IA - FORZANDO RUTA DE PRODUCCIÓN
# Eliminamos cualquier referencia a v1beta internamente
genai.configure(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")

# Usamos una configuración que suele ser más compatible con entornos antiguos de Streamlit
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

st.title("📘 Verificador de Títulos y Grados")

# 2. Carga del Excel con tus encabezados exactos
@st.cache_data
def cargar_base():
    try:
        # Lee el archivo secretarios.xlsx
        df = pd.read_excel("secretarios.xlsx")
        
        # Unimos las 3 columnas exactamente como están en tu Excel
        df['NOMBRE_COMPLETO'] = (
            df['Nombres'].astype(str) + " " + 
            df['Primer Apellido'].astype(str) + " " + 
            df['Segundo Apellido'].astype(str)
        ).str.upper().str.strip()
        
        return df
    except Exception as e:
        st.error(f"Error al cargar Excel: {e}")
        return None

df_base = cargar_base()

# 3. Interfaz de Verificación
archivo = st.file_uploader("Sube el PDF o Imagen", type=['pdf', 'jpg', 'png'])

if archivo and df_base is not None:
    st.info("🔍 Analizando documento...")
    
    try:
        with st.spinner("🤖 La IA está leyendo el nombre del secretario..."):
            bytes_data = archivo.read()
            
            # Formato de contenido explícito para evitar fallos de API
            content_parts = [
                {"mime_type": archivo.type, "data": bytes_data},
                "Identifica el nombre completo del Secretario General que firma. Responde solo el nombre."
            ]
            
            # Generar contenido
            response = model.generate_content(content_parts)
            
            nombre_ia = response.text.strip().upper()
            st.subheader(f"✍️ Autoridad detectada: {nombre_ia}")

            # --- VALIDACIÓN ADMINISTRATIVA (Punto 4: Colores) ---
            # Comparamos con la base de datos
            match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=
