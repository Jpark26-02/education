import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- CONFIGURACIÓN DIRECTA ---
MINA_LLAVE = "AIzaSyBj4e4c55ZQERlRE0itVgk8B6yU3Aw9774"
genai.configure(api_key=MINA_LLAVE)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📘 Verificador de Documentos")

# LOGIN SIMPLE PARA PRUEBAS
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u == "admin" and p == "1234":
            st.session_state.auth = True
            st.rerun()
else:
    st.success("Sesión activa")
    
    archivo = st.file_uploader("Sube el archivo aquí", type=['pdf', 'jpg', 'png', 'jpeg'])

    if archivo:
        st.write("✅ Archivo detectado en el sistema.")
        try:
            img = Image.open(archivo)
            st.image(img, width=300)
            
            with st.spinner("🤖 Gemini está analizando..."):
                # Pedimos a la IA que analice la imagen directamente
                prompt = "Analiza este documento y dime el NOMBRE del alumno y la CARRERA."
                response = model.generate_content([prompt, img])
                
                if response:
                    st.subheader("🔍 RESULTADO:")
                    st.write(response.text)
                    st.balloons()
                else:
                    st.error("La IA respondió vacío.")
                    
        except Exception as e:
            st.error(f"❌ ERROR CRÍTICO: {e}")
            st.write("Revisa los Logs en el panel de Streamlit.")
