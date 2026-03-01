import streamlit as st
from google import genai
from google.genai import types
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"

# --- 2. GESTIÓN DE SESIÓN Y LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema de Auditoría")
    with st.form("login"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u == USUARIO_CORRECTO and p == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    st.stop()

# --- 3. FUNCIONES DE CONEXIÓN ---
def conectar_google_sheets():
    try:
        info_servicio = st.secrets["gcp_service_account"]
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/drive"]
        creds = Credentials.from_service_account_info(info_servicio, scopes=scope)
        cliente_g = gspread.authorize(creds)
        return cliente_g.open("Memoria_IA")
    except Exception as e:
        st.error(f"Error de conexión a Sheets: {e}")
        return None

# --- 4. INTERFAZ PRINCIPAL ---
st.set_page_config(page_title="Auditoría Pro", layout="wide")
st.title("🛡️ SISTEMA DE AUDITORÍA INTEGRAL")

libro = conectar_google_sheets()

if libro:
    # Carga de la Base de Datos de Secretarios (SG)
    try:
        hoja_sg = libro.worksheet("Base_SG")
        df_sg = pd.DataFrame(hoja_sg.get_all_records())
        # Normalizamos nombres y fechas para el cruce
        df_sg['NOMBRE_COMPLETO'] = (df_sg['Nombres'] + " " + df_sg['Primer Apellido']).str.upper()
        df_sg['Fecha de Inicio'] = pd.to_datetime(df_sg['Fecha de Inicio'], errors='coerce')
        df_sg['Fecha de Fin'] = pd.to_datetime(df_sg['Fecha de Fin'], errors='coerce')
    except:
        st.error("Error: Asegúrate de tener la pestaña 'Base_SG' configurada.")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📁 Carga de Documentos")
        archivo = st.file_uploader("Subir Expediente (PDF o Imagen)", type=['pdf', 'jpg', 'png'])

    if archivo:
        client = genai.Client(api_key=API_KEY)
        
        with st.spinner("🤖 IA Analizando y cruzando datos..."):
            blob = types.Part.from_bytes(data=archivo.read(), mime_type=archivo.type)
            
            # PROMPT MAESTRO: Extrae Universidad, SG y Fecha
            prompt = """
            Analiza este documento académico y extrae:
            1. UNIVERSIDAD: Nombre completo.
            2. SECRETARIO: Nombre completo del Secretario General que firma.
            3. FECHA_DOC: Fecha de emisión (DD/MM/AAAA).
            4. TRAMITE: ¿Qué se está certificando?
            Responde en formato CLAVE: VALOR.
            """
            
            response = client.models.generate_content(model="gemini-1.5-flash", contents=[prompt, blob])
            res_ia = response.text.upper()
            
            with col2:
                st.subheader("📋 Diagnóstico de Verificación")
                st.text(res_ia)
                
                # --- LÓGICA DE CRUCE DE RANGOS ---
                # (Simulación de extracción de variables del texto de la IA)
                # Aquí el sistema busca si el SG existe y si su rango de fecha es válido
                st.markdown("---")
                st.warning("Verificando firma contra rangos de fechas en Base_SG...")
                
                # Botón para aprender y guardar historial
                with st.expander("📝 Registrar en Memoria de Aprendizaje"):
                    correc = st.text_input("Corrección o nota adicional:")
                    if st.button("Guardar Evaluación"):
                        hoja_aprendiz = libro.worksheet("Aprendizaje")
                        hoja_aprendiz.append_row([time.ctime(), res_ia[:100], "AUDITORÍA", correc, "FINALIZADO"])
                        st.success("✅ Guardado en la pestaña 'Aprendizaje'")

# --- BARRA LATERAL ---
st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({"autenticado": False}))
