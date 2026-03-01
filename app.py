import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time

# --- 1. CONFIGURACIÓN DE ACCESO (USUARIO Y CONTRASEÑA) ---
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"

# --- 2. CONFIGURACIÓN DE IA (CON TU LLAVE) ---
try:
    client = genai.Client(
        api_key="AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU",
        http_options={'api_version': 'v1'}
    )
except Exception as e:
    st.error(f"Error de conexión IA: {e}")

# --- 3. LÓGICA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.title("🔐 Acceso Restringido")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("⚠️ Usuario o contraseña incorrectos")

# Si no está autenticado, mostramos solo el login y paramos el resto del código
if not st.session_state.autenticado:
    login()
    st.stop()

# --- 4. CONTENIDO PROTEGIDO (SOLO SE VE SI EL LOGIN ES EXITOSO) ---
st.title("📘 Verificador de Títulos y Grados")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

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
    except:
        st.error("No se encontró el archivo 'secretarios.xlsx'")
        return None

df_base = cargar_base()

archivo = st.file_uploader("Sube el documento (PDF o Imagen)", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo and df_base is not None:
    st.info("🔍 Analizando...")
    try:
        with st.spinner("🤖 Procesando con Gemini..."):
            file_bytes = archivo.read()
            documento = types.Part.from_bytes(data=file_bytes, mime_type=archivo.type)
            
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=["Dime el nombre del secretario que firma. Solo el nombre.", documento]
