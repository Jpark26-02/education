import streamlit as st
from google import genai
from google.genai import types
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import base64
import time

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema de Auditoría")
    with st.form("login"):
        u, p = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u == USUARIO_CORRECTO and p == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Credenciales incorrectas")
    st.stop()

# --- 2. FUNCIONES AUXILIARES ---
def mostrar_pdf(file):
    base64_pdf = base64.b64encode(file.getvalue()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def conectar_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds).open("Memoria_IA")
    except: return None

# --- 3. INTERFAZ ---
st.set_page_config(page_title="Auditoría Pro", layout="wide")
st.title("🛡️ VERIFICADOR ACADÉMICO CON VISOR DIGITAL")

# --- 4. CARGA Y PREVISUALIZACIÓN ---
col_u1, col_u2 = st.columns(2)

with col_u1:
    st.info("📂 **DOCUMENTOS ACADÉMICOS**")
    doc_acad = st.file_uploader("Subir Constancia/Certificado", type=['pdf', 'jpg', 'png'], key="u_acad")
    if doc_acad and doc_acad.type == "application/pdf":
        with st.expander("👁️ Ver Documento Académico"): mostrar_pdf(doc_acad)

with col_u2:
    st.success("🎓 **DIPLOMAS**")
    doc_dip = st.file_uploader("Subir Diploma (Bachiller/Título/etc)", type=['pdf', 'jpg', 'png'], key="u_dip")
    if doc_dip and doc_dip.type == "application/pdf":
        with st.expander("👁️ Ver Diploma"): mostrar_pdf(doc_dip)

# --- 5. PROCESAMIENTO ---
if doc_acad and doc_dip:
    client = genai.Client(api_key=API_KEY)
    with st.spinner("🤖 Analizando metadatos y extrayendo campos..."):
        b_acad = types.Part.from_bytes(data=doc_acad.read(), mime_type=doc_acad.type)
        b_dip = types.Part.from_bytes(data=doc_dip.read(), mime_type=doc_dip.type)

        prompt = """
        Analiza detalladamente ambos documentos y responde estrictamente en este formato:

        TIPO_DE_ARCHIVO: [Digital / Escaneado]
        PANEL_DE_FIRMA: [Si es digital, describe si las firmas son válidas o 'Firma Desconocida'. Si es imagen, pon 'No aplica']

        --- DATOS DOCUMENTO ACADÉMICO ---
        Nombre del Estudiante: 
        Fecha de Emisión: 
        Fecha de Firma: 
        Número de Folios: 
        Facultad: 
        Escuela: 
        Especialidad: 
        Programa: 

        --- DATOS DIPLOMA ---
        Mención del Diploma: (Ej: Título Profesional de Psicología)
        Fecha de Emisión: 
        Fecha de Firma del SG: 
        Número del Diploma: 
        Nombre del Estudiante: 
        """

        response = client.models.generate_content(model="gemini-1.5-flash", contents=[prompt, b_acad, b_dip])
        res_text = response.text.upper()

        # --- MOSTRAR RESULTADOS ---
        st.divider()
        res_col, alert_col = st.columns([2, 1])

        with res_col:
            st.subheader("📋 Informe de Extracción Detallada")
            st.info(res_text)

        with alert_col:
            st.subheader("🛡️ Validación de Integridad")
            if "FIRMA_OK" in res_text or "VÁLIDA" in res_text:
                st.markdown('<div style="background-color:#00FFFF; padding:10px; border-radius:5px; color:black; font-weight:bold; text-align:center;">✓ CERTIFICADO DIGITAL VÁLIDO</div>', unsafe_allow_html=True)
            elif "DESCONOCIDA" in res_text:
                st.markdown('<div style="background-color:#FFFF00; padding:10px; border-radius:5px; color:black; font-weight:bold; text-align:center;">⚠️ FIRMA DESCONOCIDA (REVISAR)</div>', unsafe_allow_html=True)
            else:
                st.error("🚨 DOCUMENTO ESCANEADO / COPIA")
            
            st.link_button("🌐 Verificar en SUNEDU", "https://www.sunedu.gob.pe/registro-de-grados-y-titulos/")
