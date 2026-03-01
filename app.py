import streamlit as st
from google import genai
from google.genai import types
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import time

# --- 1. CONFIGURACIÓN DE SEGURIDAD (USER Y CLAVE) ---
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"

# --- 2. GESTIÓN DE SESIÓN Y LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.set_page_config(page_title="Acceso Auditoría", page_icon="🔐")
    st.title("🔐 Acceso al Sistema de Auditoría")
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u == USUARIO_CORRECTO and p == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("⚠️ Credenciales incorrectas")
    st.stop()

# --- 3. CONEXIÓN A GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        info_servicio = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(info_servicio, scopes=scope)
        return gspread.authorize(creds).open("Memoria_IA")
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None

# --- 4. INTERFAZ PRINCIPAL ---
st.set_page_config(page_title="Auditoría Académica Pro", layout="wide", page_icon="🛡️")
st.title("🛡️ VERIFICADOR ACADÉMICO INTEGRAL (SUNEDU + SG)")

libro = conectar_google_sheets()

# Cargar Base SG para cruce
df_sg = pd.DataFrame()
if libro:
    try:
        df_sg = pd.DataFrame(libro.worksheet("Base_SG").get_all_records())
        df_sg['NOMBRE_SG'] = (df_sg['Nombres'] + " " + df_sg['Primer Apellido']).str.upper()
    except:
        st.warning("⚠️ No se pudo cargar 'Base_SG'. Verifica los nombres de las columnas.")

# --- 5. PANELES DE CARGA ---
st.markdown("### 📑 Carga de Expedientes")
col1, col2 = st.columns(2)
with col1:
    st.info("**1. DOCUMENTOS ACADÉMICOS** (Constancias/Certificados)")
    doc_academico = st.file_uploader("Subir archivo", type=['pdf', 'jpg', 'png'], key="acad")
with col2:
    st.success("**2. DIPLOMAS** (Bachiller/Título/Maestría/Doctorado)")
    doc_diploma = st.file_uploader("Subir archivo", type=['pdf', 'jpg', 'png'], key="dip")

# --- 6. PROCESAMIENTO E IA ---
if doc_academico and doc_diploma:
    try:
        client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})
        
        with st.spinner("🤖 Analizando firmas, integridad y datos SUNEDU..."):
            blob_acad = types.Part.from_bytes(data=doc_academico.read(), mime_type=doc_academico.type)
            blob_dip = types.Part.from_bytes(data=doc_diploma.read(), mime_type=doc_diploma.type)

            prompt = """
            Actúa como un Auditor Académico y Perito Digital.
            
            IDENTIFICACIÓN DE FIRMA:
            - Si el documento es digital y la firma es válida -> "RESULTADO: FIRMA_OK"
            - Si la firma digital dice 'Desconocida' o 'No Validada' pero el documento es íntegro -> "RESULTADO: FIRMA_DESCONOCIDA"
            - Si el documento es un escaneado o foto -> "RESULTADO: FIRMA_IMAGEN"
            
            EXTRACCIÓN:
            - Titular (Nombre completo y DNI si existe).
            - Universidad y Tipo de Grado.
            - Nombre del Secretario General (SG) que firma.
            - Fecha de Emisión.
            """

            response = client.models.generate_content(model="gemini-1.5-flash", contents=[prompt, blob_acad, blob_dip])
            res_ia = response.text.upper()

            # --- LÓGICA DE ALERTAS VISUALES ---
            st.divider()
            
            if "FIRMA_OK" in res_ia:
                st.balloons()
                st.markdown('<div style="background-color:#00FFFF; padding:20px; border-radius:10px; color:black; text-align:center; font-weight:bold;">✅ FIRMA VÁLIDA: PROCEDER CON VALIDACIÓN SUNEDU</div>', unsafe_allow_html=True)
            
            elif "FIRMA_DESCONOCIDA" in res_ia:
                st.markdown('<div style="background-color:#FFFF00; padding:20px; border-radius:10px; color:black; text-align:center; font-weight:bold;">🟡 ADVERTENCIA: FIRMA DESCONOCIDA (REVISIÓN VISUAL OK - SÍ PROCEDE)</div>', unsafe_allow_html=True)
            
            else:
                st.error("🚨 ALERTA: Documento detectado como COPIA SIMPLE / ESCANEADO. No es un original digital.")

            # Mostrar informe y acciones
            res_col, side_col = st.columns([2,
