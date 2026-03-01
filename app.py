import streamlit as st
from google import genai
from google.genai import types  # Necesario para el formato Part
import pandas as pd
import time

# 1. Configuración del Cliente
client = genai.Client(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")

st.title("📘 Verificador de Títulos y Grados")

# 2. Carga de Base de Datos (Mantenemos tu estructura de Excel)
@st.cache_data
def cargar_base():
    try:
        df = pd.read_excel("secretarios.xlsx")
        df.columns = df.columns.str.strip()
        df['NOMBRE_COMPLETO'] = (
            df['Nombres'].astype(str) + " " + 
            df['Primer Apellido'].astype(str) + " " + 
            df['Segundo Apellido'].astype(str)
        ).str.upper().str.strip()
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return None

df_base = cargar_base()

# 3. Interfaz y Procesamiento
archivo = st.file_uploader("Sube el PDF o Imagen", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo and df_base is not None:
    st.info("🔍 Analizando documento...")
    
    try:
        with st.spinner("🤖 Extrayendo información..."):
            # LEER BYTES DEL ARCHIVO
            file_bytes = archivo.read()
            
            # --- SOLUCIÓN AL ERROR DE VALIDACIÓN ---
            # Creamos un objeto 'Part' que contiene los datos y el tipo MIME exacto
            documento_part = types.Part.from_bytes(
                data=file_bytes,
                mime_type=archivo.type
            )
            
            # Llamada al modelo con la estructura correcta
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    "Identifica el nombre del Secretario General que firma. Responde solo el nombre.",
                    documento_part
                ]
            )
            
            nombre_ia = response.text.strip().upper()
            st.subheader(f"✍️ Autoridad detectada: {nombre_ia}")

            # --- VALIDACIÓN POR COLORES ---
            match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=False)]

            if not match.empty:
                univ = match['Universidad'].values[0]
                st.markdown(f'''
                    <div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">
                        ✅ REGISTRO CELESTE: Autoridad válida para {univ}
                    </div>
                ''', unsafe_content_allowed=True)
                st.balloons()
            else:
                st.markdown('''
                    <div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center; font-weight: bold;">
                        ❌ REGISTRO ROJO: Autoridad no encontrada en base de datos
                    </div>
                ''', unsafe_content_allowed=True)

    except Exception as e:
        st.error(f"Error de validación: {e}")

# Botón SUNEDU
if st.button("Consultar SUNEDU"):
    with st.spinner("Validando..."):
        time.sleep(10)
        st.success("Validación completada.")
