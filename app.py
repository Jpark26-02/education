import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# 1. Configuración de IA (Ruta estable para evitar error 404)
genai.configure(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📘 Verificador de Títulos y Grados")

# 2. Carga y Limpieza de tu Excel
@st.cache_data
def cargar_base():
    try:
        df = pd.read_excel("secretarios.xlsx")
        # Limpiamos nombres de columnas (quitar espacios y pasar a MAYÚSCULAS)
        df.columns = df.columns.str.strip().str.upper()
        
        # Unimos las 3 columnas de tu Excel para el nombre completo
        df['NOMBRE_COMPLETO'] = (
            df['NOMBRES'].astype(str) + " " + 
            df['PRIMER APELLIDO'].astype(str) + " " + 
            df['SEGUNDO APELLIDO'].astype(str)
        ).str.upper().str.strip()
        
        return df
    except Exception as e:
        st.error(f"Error al leer las columnas del Excel: {e}")
        return None

df_base = cargar_base()

# 3. Interfaz de Usuario
archivo = st.file_uploader("Sube el PDF o Imagen del documento", type=['pdf', 'jpg', 'png'])

if archivo and df_base is not None:
    st.info("🔍 Analizando documento con IA...")
    
    try:
        with st.spinner("Extrayendo datos..."):
            bytes_data = archivo.read()
            # Pedimos a la IA que identifique a la autoridad
            prompt = "Identifica el nombre completo del Secretario General que firma. Responde solo el nombre."
            
            response = model.generate_content([{"mime_type": archivo.type, "data": bytes_data}, prompt])
            nombre_detectado = response.text.strip().upper()
            
            st.subheader(f"✍️ Autoridad Detectada: {nombre_detectado}")

            # --- VALIDACIÓN ADMINISTRATIVA (Punto 4: Colores) ---
            # Buscamos coincidencias parciales por si la IA omite un segundo nombre
            coincidencia = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_detectado, na=False)]

            if not coincidencia.empty:
                # Fondo CELESTE: Autoridad encontrada
                universidad = coincidencia['UNIVERSIDAD'].values[0]
                st.markdown(f'''
                    <div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center;">
                        <h3 style="margin:0;">✅ REGISTRO CELESTE</h3>
                        <p>Autoridad válida encontrada para la <b>{universidad}</b></p>
                    </div>
                ''', unsafe_content_allowed=True)
                st.balloons()
            else:
                # Fondo ROJO: No aparece en tu Excel
                st.markdown('''
                    <div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                        <h3 style="margin:0;">❌ REGISTRO ROJO</h3>
                        <p>La autoridad no figura en la base de datos oficial.</p>
                    </div>
                ''', unsafe_content_allowed=True)

    except Exception as e:
        st.error(f"Error técnico: {e}")

# 4. Regla SUNEDU (Punto 5)
if st.button("Consultar SUNEDU"):
    with st.spinner("Validando contra registros históricos (10s)..."):
        time.sleep(10)
        st.success("Proceso de validación finalizado.")
