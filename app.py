import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd

# Configuración visual de la página
st.set_page_config(page_title="Verificador de Documentos", page_icon="📄")

# --- SISTEMA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso Restringido")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if usuario == "admin" and clave == "1234":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
else:
    # --- PANEL PRINCIPAL UNA VEZ LOGUEADO ---
    st.title("📄 Verificador de Documentos Inteligente")
    st.success("Sesión iniciada correctamente.")

    archivo = st.file_uploader("Sube tu PDF o Imagen para validar", type=['pdf', 'jpg', 'png', 'jpeg'])

    if archivo:
        st.info("Procesando documento... por favor espera.")
        # Aquí iría la lógica de OCR que programaremos a continuación
        img = Image.open(archivo)
        st.image(img, caption="Vista previa del documento", use_container_width=True)
        
        # Botón para simular la validación
        if st.button("Validar Firmas y Sellos"):
            st.warning("Analizando coherencia de datos con SUNEDU...")
            st.balloons()
            st.success("Análisis completado: Documento con alta probabilidad de autenticidad.")
