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
    st.set_page_config(page_title="Login - Auditoría", page_icon="🔐")
    st.title("🔐 Acceso al Sistema de Auditoría")
    
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

# Barra lateral
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

st.title("🛡️ SISTEMA DE AUDITORÍA INTEGRAL (SG + MEMORIA)")

libro = conectar_google_sheets()

if libro:
    try:
        hoja_sg = libro.worksheet("Base_SG")
        df_sg = pd.DataFrame(hoja_sg.get_all_records())
        df_sg['NOMBRE_COMPLETO'] = (df_sg['Nombres'] + " " + df_sg['Primer Apellido']).str.upper()
        df_sg['Fecha de Inicio'] = pd.to_datetime(df_sg['Fecha de Inicio'], errors='coerce')
        df_sg['Fecha de Fin'] = pd.to_datetime(df_sg['Fecha de Fin'], errors='coerce')
    except Exception as e:
        st.error(f"⚠️ Error en pestaña 'Base_SG': {e}")
        st.stop()

    # --- 5. CARGA DE ARCHIVOS (Aquí estaba el error de sangría) ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📁 Carga de Expediente")
        constancia = st.file_uploader("Subir Constancia Maestra", type=['pdf', 'jpg', 'png'])
        anexos = st.file_uploader("Subir Anexos", type=['pdf', 'jpg', 'png'], accept_multiple_files=True)

    if constancia and anexos:
        try:
            client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})
            
            with st.spinner("🤖 IA analizando..."):
                blob_c = types.Part.from_bytes(data=constancia.read(), mime_type=constancia.type)
                
                prompt_auditoria = """
                Analiza la CONSTANCIA y los anexos:
                1. UNIVERSIDAD: Nombre.
                2. SECRETARIO: Nombre completo.
                3. FECHA_DOC: DD/MM/AAAA.
                4. TRAMITE: Tipo de Grado.
                5. ANEXOS: Documentos hallados.
                """
                
                response = client.models.generate_content(model="gemini-1.5-flash", contents=[prompt_auditoria, blob_c])
                res_ia = response.text.upper()
                
                with col2:
                    st.subheader("📋 Diagnóstico")
                    st.code(res_ia)
                    
                    st.divider()
                    st.subheader("🧠 Entrenar Memoria")
                    correccion = st.text_input("Corrección si la IA falló:")
                    
                    if st.button("💾 Guardar en Aprendizaje"):
                        hoja_apr = libro.worksheet("Aprendizaje")
                        hoja_apr.append_row([time.ctime(), res_ia[:100], "IA", correccion, "OK"])
                        st.success("¡Guardado!")

        except Exception as e:
            st.error(f"Error al procesar: {e}")
else:
    st.info("Configura la conexión a Google Sheets para comenzar.")
