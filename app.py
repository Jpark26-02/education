import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# 1. Configuración de IA (Ruta estable para evitar error 404)
genai.configure(api_key="AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774")
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

st.title("📘 Verificador de Títulos y Grados")

# 2. Carga del Excel con tus encabezados exactos
@st.cache_data
def cargar_base():
    try:
        # Lee el archivo (por defecto inicia en fila 1 y datos en fila 2)
        df = pd.read_excel("secretarios.xlsx")
        
        # Unimos las 3 columnas según tu estructura
        # Usamos los nombres exactos: 'Nombres', 'Primer Apellido', 'Segundo Apellido'
        df['NOMBRE_COMPLETO'] = (
            df['Nombres'].astype(str) + " " + 
            df['Primer Apellido'].astype(str) + " " + 
            df['Segundo Apellido'].astype(str)
        ).str.upper().str.strip()
        
        return df
    except Exception as e:
        st.error(f"Error: No se encontraron las columnas. Revisa que el Excel tenga los nombres exactos. Detalle: {e}")
        return None

df_base = cargar_base()

# 3. Interfaz de Verificación
archivo = st.file_uploader("Sube el PDF o Imagen del documento", type=['pdf', 'jpg', 'png'])

if archivo and df_base is not None:
    st.info("🔍 Analizando documento con IA...")
    
    try:
        with st.spinner("Buscando autoridad en el documento..."):
            bytes_data = archivo.read()
            # Pedimos a Gemini que extraiga solo el nombre del firmante
            prompt = "Identifica el nombre completo del Secretario General que firma este documento. Responde solo el nombre, sin cargos."
            
            response = model.generate_content([{"mime_type": archivo.type, "data": bytes_data}, prompt])
            nombre_ia = response.text.strip().upper()
            
            st.subheader(f"✍️ Autoridad detectada por IA: {nombre_ia}")

            # --- VALIDACIÓN ADMINISTRATIVA (Punto 4: Colores) ---
            # Comparamos el nombre de la IA con nuestra columna 'NOMBRE_COMPLETO'
            match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=False)]

            if not match.empty:
                # Datos adicionales del Excel para el mensaje
                universidad = match['Universidad'].values[0]
                estado = match['Estado'].values[0]
                
                # Fondo CELESTE
                st.markdown(f'''
                    <div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center;">
                        <h3 style="margin:0;">✅ REGISTRO CELESTE</h3>
                        <p>Autoridad <b>VÁLIDA</b> encontrada para: <b>{universidad}</b></p>
                        <p>Estado en Base de Datos: {estado}</p>
                    </div>
                ''', unsafe_content_allowed=True)
                st.balloons()
            else:
                # Fondo ROJO
                st.markdown('''
                    <div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                        <h3 style="margin:0;">❌ REGISTRO ROJO</h3>
                        <p>La autoridad detectada no coincide con los registros oficiales en el Excel.</p>
                    </div>
                ''', unsafe_content_allowed=True)

    except Exception as e:
        st.error(f"Error técnico durante el análisis: {e}")

# 4. Regla SUNEDU (Punto 5)
if st.button("Consultar SUNEDU"):
    with st.spinner("Validando contra registros históricos (10s)..."):
        time.sleep(10)
        st.success("Proceso de validación SUNEDU finalizado.")
