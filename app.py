import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time

# --- 1. CONFIGURACIÓN DE ACCESO ---
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"

# --- 2. CONFIGURACIÓN DE IA ---
try:
    client = genai.Client(
        api_key="AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU",
        http_options={'api_version': 'v1'}
    )
except Exception as e:
    st.error(f"Error de conexión IA: {e}")

# --- 3. LÓGICA DE LOGIN (Simplificada) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso Restringido")
    with st.form("login_form"):
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        submit = st.form_submit_state = st.form_submit_button("Ingresar")
        
        if submit:
            if user == USUARIO_CORRECTO and pw == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.success("Acceso concedido. Cargando...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("⚠️ Credenciales incorrectas")
    st.stop()

# --- 4. CONTENIDO PROTEGIDO ---
st.title("📘 Verificador de Títulos y Grados")

# Botón para salir en la barra lateral
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

@st.cache_data
def cargar_base():
    try:
        # Asegúrate de que 'secretarios.xlsx' esté en la misma carpeta en GitHub
        df = pd.read_excel("secretarios.xlsx")
        df.columns = df.columns.str.strip()
        df['NOMBRE_COMPLETO'] = (
            df['Nombres'].astype(str) + " " + 
            df['Primer Apellido'].astype(str) + " " + 
            df['Segundo Apellido'].astype(str)
        ).str.upper().str.strip()
        return df
    except Exception as e:
        st.error(f"Error: No se pudo cargar 'secretarios.xlsx'. Verifica el nombre del archivo. ({e})")
        return None

df_base = cargar_base()

archivo = st
