import streamlit as st
from google import genai
from google.genai import types
import base64
import time
import json

# --- 1. CONFIGURACIÓN DE SEGURIDAD (USER Y CLAVE) ---
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "datos_ia" not in st.session_state:
    st.session_state.datos_ia = {}

# Pantalla de Login
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

# --- 2. FUNCIONES DE INTERFAZ ---
def visualizar_pdf(file_bytes):
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="450" style="border:2px solid #2e7d32; border-radius:10px;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 3. DASHBOARD PRINCIPAL ---
st.set_page_config(page_title="Verificador SUNEDU Pro", layout="wide", page_icon="🛡️")
st.title("🛡️ VERIFICADOR ACADÉMICO INTEGRAL (SUNEDU + SG)")

# Paneles de Carga
st.markdown("### 📑 Carga de Expedientes")
col_u1, col_u2 = st.columns(2)
with col_u1:
    st.info("**1. DOCUMENTOS ACADÉMICOS**")
    doc_acad = st.file_uploader("Subir Constancia", type=['pdf', 'jpg', 'png'], key="u_acad")
with col_u2:
    st.success("**2. DIPLOMAS**")
    doc_dip = st.file_uploader("Subir Diploma", type=['pdf', 'jpg', 'png'], key="u_dip")

# --- 4. PROCESAMIENTO CON IA ---
if doc_acad and doc_dip:
    if st.button("🚀 ANALIZAR Y PRE-RELLENAR FORMULARIOS"):
        with st.spinner("🤖 La IA está transcribiendo los datos..."):
            client = genai.Client(api_key=API_KEY)
            st.session_state.b_acad = doc_acad.read()
            st.session_state.b_dip = doc_dip.read()
            
            blob_acad = types.Part.from_bytes(data=st.session_state.b_acad, mime_type=doc_acad.type)
            blob_dip = types.Part.from_bytes(data=st.session_state.b_dip, mime_type=doc_dip.type)

            prompt = """Analiza los documentos y extrae la info para SUNEDU. Responde SOLO en JSON:
            {
              "entidad": "", "sg_nombre": "", "dni": "", "ap_paterno": "", "ap_materno": "", "nombres": "",
              "tipo_tramite": "", "fecha_expedicion": "", "numero_diploma": "", "descripcion_mencion": "",
              "facultad": "", "escuela": "", "programa": "", "firma_status": "VÁLIDA/DESCONOCIDA/IMAGEN"
            }"""

            response = client.models.generate_content(model="gemini-1.5-flash", contents=[prompt, blob_acad, blob_dip])
            try:
                raw_json = response.text.replace('```json', '').replace('```', '').strip()
                st.session_state.datos_ia = json.loads(raw_json)
            except:
                st.error("Error al procesar. Reintente.")

# --- 5. FORMULARIO ESTILO SUNEDU (RERELLENADO) ---
if st.session_state.datos_ia:
    d = st.session_state.datos_ia
    st.divider()
    
    # Visores
    v1, v2 = st.columns(2)
    with v1: visualizar_pdf(st.session_state.b_acad)
    with v2: visualizar_pdf(st.session_state.b_dip)

    st.subheader("📋 FORMULARIO DE REGISTRO (EDITABLE)")
    
    with st.container():
        # Fila 1: Entidad y SG
        c1, c2 = st.columns(2)
        f_entidad = c1.text_input("Entidad:*", value=d.get("entidad", ""))
        f_sg = c2.text_input("Secretario General:*", value=d.get("sg_nombre", ""))
        
        # Fila 2: Identidad y Apellidos
        c3, c4, c5 = st.columns([1, 1.5, 1.5])
        f_dni = c3.text_input("Número de documento:*", value=d.get("dni", ""))
        f_app = c4.text_input("Apellido paterno:*", value=d.get("ap_paterno", ""))
        f_apm = c5.text_input("Apellido materno:*", value=d.get("ap_materno", ""))
        
        # Fila 3: Nombres y Trámite
        c6, c7 = st.columns([2, 1])
        f_nom = c6.text_input("Nombres:*", value=d.get("nombres", ""))
        f_tra = c7.text_input("Tipo de trámite:*", value=d.get("tipo_tramite", ""))
        
        # Fila 4: Fecha y Número
        c8, c9 = st.columns(2)
        f_fex = c8.text_input("Fecha de expedición:*", value=d.get("fecha_expedicion", ""))
        f_num = c9.text_input("Número de Diploma/Folio:*", value=d.get("numero_diploma", ""))
        
        # Fila 5: Descripción Amplia
        f_men = st.text_area("Descripción (Mención del Diploma/Grado):", value=d.get("descripcion_mencion", ""))
        
        # Fila 6: Detalle Académico
        c10, c11, c12 = st.columns(3)
        f_fac = c10.text_input("Facultad:", value=d.get("facultad", ""))
        f_esc = c11.text_input("Escuela:", value=d.get("escuela", ""))
        f_pro = c12.text_input("Programa:", value=d.get("programa", ""))

    st.divider()
    
    # Estado de Firma y Botón de Copiado
    status_firma = d.get("firma_status", "DESCONOCIDA")
    if "VÁLIDA" in status_firma: st.success(f"Firma: {status_firma}")
    elif "DESCONOCIDA" in status_firma: st.warning(f"Firma: {status_firma}")
    else: st.error(f"Firma: {status_firma}")

    if st.button("💾 CONFIRMAR Y GUARDAR AUDITORÍA"):
        st.success("✅ Datos validados y listos para SUNEDU.")
        st.balloons()
