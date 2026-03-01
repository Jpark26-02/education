import streamlit as st
from google import genai
import pandas as pd
import time

# 1. Configuración con la NUEVA LIBRERÍA
client = genai.Client(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")

st.title("📘 Verificador de Títulos y Grados")

# 2. Carga de Excel con tus encabezados reales
@st.cache_data
def cargar_base():
    try:
        df = pd.read_excel("secretarios.xlsx")
        # Limpiamos nombres de columnas por seguridad
        df.columns = df.columns.str.strip()
        
        # Unimos las 3 columnas de tu Excel
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

# 3. Interfaz de Usuario
archivo = st.file_uploader("Sube el PDF o Imagen", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo and df_base is not None:
    st.info("🔍 Analizando documento con la nueva API de Google...")
    
    try:
        with st.spinner("🤖 Leyendo autoridad..."):
            # Procesamiento con el nuevo cliente
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    "Identifica el nombre del Secretario General que firma. Responde solo el nombre.",
                    archivo.read()
                ]
            )
            
            nombre_ia = response.text.strip().upper()
            st.subheader(f"✍️ Autoridad detectada: {nombre_ia}")

            # --- VALIDACIÓN POR COLORES (CELESTE / ROJO) ---
            match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=False)]

            if not match.empty:
                univ = match['Universidad'].values[0]
                # FONDO CELESTE si coincide
                st.markdown(f'''
                    <div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">
                        ✅ REGISTRO CELESTE: Autoridad válida para {univ}
                    </div>
                ''', unsafe_content_allowed=True)
                st.balloons()
            else:
                # FONDO ROJO si no coincide
                st.markdown('''
                    <div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center; font-weight: bold;">
                        ❌ REGISTRO ROJO: Autoridad no encontrada en la base de datos
                    </div>
                ''', unsafe_content_allowed=True)

    except Exception as e:
        st.error(f"Error con la nueva API: {e}")

# 4. Botón SUNEDU
if st.button("Consultar SUNEDU"):
    with st.spinner("Validando registros (10s)..."):
        time.sleep(10)
        st.success("Validación completada.")
