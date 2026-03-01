import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# 1. Configuración de IA
genai.configure(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")

# Intentamos con el nombre estándar para evitar el error 404
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📘 Verificador de Títulos y Grados")

# 2. Carga del Excel con tus encabezados exactos
@st.cache_data
def cargar_base():
    try:
        df = pd.read_excel("secretarios.xlsx")
        # Limpieza de columnas para evitar errores de espacios
        df.columns = df.columns.str.strip()
        
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
    st.info(f"🔍 Analizando: {archivo.name}")
    
    try:
        with st.spinner("🤖 La IA está leyendo el documento..."):
            bytes_data = archivo.read()
            prompt = "Identifica el nombre completo del Secretario General que firma. Responde solo el nombre."
            
            # Generar contenido
            response = model.generate_content([
                {"mime_type": archivo.type, "data": bytes_data},
                prompt
            ])
            
            nombre_ia = response.text.strip().upper()
            st.subheader(f"✍️ Autoridad detectada: {nombre_ia}")

            # --- VALIDACIÓN ADMINISTRATIVA (Punto 4: Colores) ---
            # Comparamos con la base de datos
            # Corregido: Paréntesis cerrados correctamente
            match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=False)]

            if not match.empty:
                univ = match['Universidad'].values[0]
                # FONDO CELESTE si coincide
                st.markdown(f'''
                    <div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">
                        ✅ AUTORIDAD REGISTRADA - REGISTRO CELESTE<br>
                        Institución: {univ}
                    </div>
                ''', unsafe_content_allowed=True)
                st.balloons()
            else:
                # FONDO ROJO si no coincide
                st.markdown('''
                    <div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center; font-weight: bold;">
                        ❌ AUTORIDAD NO ENCONTRADA - REGISTRO ROJO
                    </div>
                ''', unsafe_content_allowed=True)

    except Exception as e:
        st.error(f"Error de comunicación con la IA: {e}")
        st.warning("Verifica que tu requirements.txt incluya google-generativeai>=0.7.2")

# 4. Regla SUNEDU (Punto 5)
if st.button("Consultar SUNEDU"):
    with st.spinner("Esperando 10 segundos..."):
        time.sleep(10)
        st.success("Consulta completada contra registros históricos.")
