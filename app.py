import streamlit as st
from google import genai
from google.genai import types
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
# Cambia estos valores por los que desees usar
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"

# --- 2. GESTIÓN DE SESIÓN Y LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.set_page_config(page_title="Login - Auditoría", page_icon="🔐")
    st.title("🔐 Acceso al Sistema de Auditoría")
    st.markdown("Introduce tus credenciales para gestionar la base de datos y la IA.")
    
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u == USUARIO_CORRECTO and p == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("⚠️ Usuario o contraseña incorrectos")
    st.stop()

# --- 3. FUNCIONES DE CONEXIÓN A GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        # Esto lee el JSON configurado en Settings > Secrets de Streamlit
        info_servicio = st.secrets["gcp_service_account"]
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/drive"]
        creds = Credentials.from_service_account_info(info_servicio, scopes=scope)
        cliente_g = gspread.authorize(creds)
        return cliente_g.open("Memoria_IA")
    except Exception as e:
        st.error(f"❌ Error de conexión a Google Sheets: {e}")
        return None

# --- 4. CONFIGURACIÓN DE PÁGINA PRINCIPAL ---
st.set_page_config(page_title="Auditoría Académica Pro", layout="wide", page_icon="🛡️")

# Botón para cerrar sesión en la barra lateral
st.sidebar.title("Configuración")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

st.title("🛡️ SISTEMA DE AUDITORÍA INTEGRAL (SG + MEMORIA)")
st.markdown("Validación de Constancias, Anexos y Vigencia de Autoridades.")

# Cargar el libro de Google Sheets
libro = conectar_google_sheets()

if libro:
    # Intentar cargar la Base de Datos de Secretarios Generales (SG)
    try:
        hoja_sg = libro.worksheet("Base_SG")
        datos_sg = hoja_sg.get_all_records()
        df_sg = pd.DataFrame(datos_sg)
        
        # Normalizar nombres para facilitar la búsqueda
        df_sg['NOMBRE_COMPLETO'] = (df_sg['Nombres'] + " " + df_sg['Primer Apellido']).str.upper()
        # Convertir fechas a formato datetime para comparaciones
        df_sg['Fecha de Inicio'] = pd.to_datetime(df_sg['Fecha de Inicio'], errors='coerce')
        df_sg['Fecha de Fin'] = pd.to_datetime(df_sg['Fecha de Fin'], errors='coerce')
    except Exception as e:
        st.error(f"⚠️ Error al leer la pestaña 'Base_SG': {e}")
        st.info("Asegúrate de que la pestaña 'Base_SG' exista y tenga los encabezados correctos.")
        st.stop()

    # --- 5. CARGA DE ARCHIVOS ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
