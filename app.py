import streamlit as st
from google import genai
from google.genai import types
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import base64
import time

# --- 1. SEGURIDAD Y CONFIGURACIÓN ---
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"

st.set_page_config(page_title="Auditoría Académica Pro", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema")
    with st.form("login"):
        u, p = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u == USUARIO_CORRECTO and p == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Credenciales incorrectas")
    st.stop()

# --- 2. FUNCIONES DE APOYO ---
def conectar_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds).open("Memoria_IA")
    except: return None

def get_pdf_display(file):
    base64_pdf = base64.b64encode(file.getvalue()).decode('utf-8')
    return f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf">'

# --- 3. INTERFAZ DE CARGA ---
st.title("🛡️ SISTEMA DE AUDITORÍA CON CAMPOS EDITABLES")
libro = conectar_sheets()

col_u1, col_u2 = st.columns(2)
with col_u1:
    st.info("📂 **DOC. ACADÉMICOS**")
    doc_acad = st.file_uploader("Subir Constancia", type=['pdf', 'jpg', 'png'], key="u_acad")
with col_u2:
    st.success("🎓 **DIPLOMAS**")
    doc_dip = st.file_uploader("Subir Diploma", type=['pdf', 'jpg', 'png'], key="u_dip")

# --- 4. PROCESAMIENTO E IA ---
if doc_acad and doc_dip:
    client = genai.Client(api_key=API_KEY)
    
    # Botón para disparar la IA
    if st.button("🔍 INICIAR AUDITORÍA E IDENTIFICAR DATOS"):
        with st.spinner("Analizando documentos..."):
            b_acad = types.Part.from_bytes(data=doc_acad.read(), mime_type=doc_acad.type)
            b_dip = types.Part.from_bytes(data=doc_dip.read(), mime_type=doc_dip.type)

            prompt = """Extrae los datos y responde en formato JSON plano:
            {
            "tipo_archivo": "", "panel_firma": "",
            "acad_estudiante": "", "acad_emision": "", "acad_firma": "", "acad_folios": "", "acad_facultad": "", "acad_escuela": "", "acad_especialidad": "", "acad_programa": "",
            "dip_mencion": "", "dip_emision": "", "dip_firma_sg": "", "dip_numero": "", "dip_estudiante": ""
            }"""

            response = client.models.generate_content(model="gemini-1.5-flash", contents=[prompt, b_acad, b_dip])
            # Intentamos parsear la respuesta (simplificado para este ejemplo)
            st.session_state.datos_ia = response.text
            st.session_state.auditado = True

    # --- 5. VISORES Y FORMULARIO EDITABLE ---
    if "auditado" in st.session_state:
        st.divider()
        v1, v2 = st.columns(2)
        with v1: 
            st.markdown("### Visor Documento Académico")
            st.markdown(get_pdf_display(doc_acad), unsafe_allow_html=True)
        with v2: 
            st.markdown("### Visor Diploma")
            st.markdown(get_pdf_display(doc_dip), unsafe_allow_html=True)

        st.divider()
        st.subheader("📝 VALIDACIÓN Y EDICIÓN DE DATOS")
        st.warning("Verifica los datos extraídos por la IA. Puedes editarlos directamente si hay errores.")
        
        # FORMULARIO EDITABLE
        with st.form("form_datos"):
            f1, f2 = st.columns(2)
            with f1:
                st.markdown("**DATOS ACADÉMICOS**")
                n_est = st.text_input("Nombre Estudiante", value="")
                f_emi = st.text_input("Fecha Emisión Acad.", value="")
                f_fac = st.text_input("Facultad", value="")
                f_esc = st.text_input("Escuela", value="")
                f_prog = st.text_input("Programa", value="")
                f_fol = st.text_input("N° Folios", value="")
            
            with f2:
                st.markdown("**DATOS DIPLOMA**")
                d_men = st.text_input("Mención Diploma", value="")
                d_num = st.text_input("N° Diploma", value="")
                d_emi = st.text_input("Fecha Emisión Diploma", value="")
                d_sg = st.text_input("Firma SG", value="")
                d_est = st.text_input("Estudiante en Diploma", value="")

            st.markdown("**ESTADO TÉCNICO**")
            status = st.selectbox("Estado de Firma Digital", ["FIRMA VÁLIDA", "FIRMA DESCONOCIDA", "ESCANEADO/IMAGEN"])

            if st.form_submit_button("💾 GUARDAR AUDITORÍA FINAL"):
                if libro:
                    libro.worksheet("Aprendizaje").append_row([
                        time.ctime(), n_est, d_men, status, "VALIDADO MANUAL"
                    ])
                    st.success("✅ ¡Auditoría guardada exitosamente!")
                    st.balloons()
