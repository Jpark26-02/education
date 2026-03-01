import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# 1. Configuración de la API con clave directa
genai.configure(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📘 Verificador de Títulos y Grados")

# 2. Carga y limpieza de base de datos Excel
@st.cache_data
def cargar_datos():
    try:
        # Cargamos el archivo que debe estar en la misma carpeta que app.py
        df = pd.read_excel("secretarios.xlsx")
        
        # Unimos las columnas de tu Excel para crear el nombre completo
        df['NOMBRE_COMPLETO'] = (
            df['Nombres'].astype(str) + " " + 
            df['Primer Apellido'].astype(str) + " " + 
            df['Segundo Apellido'].astype(str)
        ).str.upper().str.strip()
        
        return df
    except Exception as e:
        st.error(f"Error al cargar el Excel: {e}")
        return None

df_base = cargar_datos()

# 3. Área de carga de documentos
archivo = st.file_uploader("Sube el PDF o Imagen del diploma", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo and df_base is not None:
    st.info(f"📂 Archivo '{archivo.name}' recibido. Analizando...")
    
    try:
        with st.spinner("🤖 Extrayendo información con IA..."):
            bytes_data = archivo.read()
            prompt = "Identifica el nombre completo del Secretario General que firma este documento. Responde SOLO el nombre."
            
            # Llamada a la IA corrigiendo el formato de contenido
            response = model.generate_content([
                {"mime_type": archivo.type, "data": bytes_data},
                prompt
            ])
            
            nombre_ia = response.text.strip().upper()
            st.subheader(f"✍️ Autoridad detectada: {nombre_ia}")

            # --- VALIDACIÓN DE COLOR (PUNTO 4) ---
            # Buscamos el nombre extraído dentro de nuestra columna combinada
            # Línea corregida: todos los paréntesis cerrados
            match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=False)]

            if not match.empty:
                # Si existe -> Registro CELESTE
                universidad = match['Universidad'].values[0]
                st.markdown(f'''
                    <div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">
                        ✅ AUTORIDAD VIGENTE - REGISTRO CELESTE<br>
                        Institución: {universidad}
                    </div>
                ''', unsafe_content_allowed=True)
                st.balloons()
            else:
                # Si NO existe -> Registro ROJO
                st.markdown('''
                    <div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center; font-weight: bold;">
                        ❌ AUTORIDAD NO RECONOCIDA - REGISTRO ROJO<br>
                        Verifique la validez del documento.
                    </div>
                ''', unsafe_content_allowed=True)

    except Exception as e:
        st.error(f"Error de comunicación con la IA: {e}")

# 4. Botón de simulación SUNEDU (Punto 5)
if st.button("Consultar SUNEDU"):
    with st.spinner("Conectando con registros históricos (espera 10s)..."):
        time.sleep(10)
        st.success("Validación completada.")
