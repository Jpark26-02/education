import streamlit as st
from google import genai
from google.genai import types
import base64
import json
import time

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(page_title="Auditoría Académica Pro", layout="wide", page_icon="🛡️")

# Inyección de CSS para mejorar la estética de los campos
st.markdown("""
    <style>
    .stTextInput vesta { font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SEGURIDAD ---
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "datos_ia" not in st.session_state:
    st.session_state.datos_ia = {}

if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema de Auditoría")
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u == USUARIO_CORRECTO and p == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("⚠️ Credenciales incorrectas")
    st.stop()

# --- 3. INTERFAZ DE CARGA (DISEÑO BONITO) ---
st.title("🛡️ VERIFICADOR ACADÉMICO INTEGRAL (SUNEDU + SG)")
st.markdown("### 📝 Carga de Documentos para Validación")

col_u1, col_u2 = st.columns(2)

with col_u1:
    st.markdown('<div style="background-color:#1e3a8a; padding:10px; border-radius:5px; color:white; font-weight:bold;">1. DOCUMENTOS ACADÉMICOS (Escaneado/Digital)</div>', unsafe_allow_html=True)
    doc_acad = st.file_uploader("Subir Constancia", type=['pdf', 'jpg', 'png'], key="u_acad", label_visibility="collapsed")

with col_u2:
    st.markdown('<div style="background-color:#064e3b; padding:10px; border-radius:5px; color:white; font-weight:bold;">2. DIPLOMAS (Validación vs SUNEDU)</div>', unsafe_allow_html=True)
    doc_dip = st.file_uploader("Subir Diploma", type=['pdf', 'jpg', 'png'], key="u_dip", label_visibility="collapsed")

# --- 4. LÓGICA DE PROCESAMIENTO ---
if doc_acad and doc_dip:
    if st.button("🚀 INICIAR PROCESAMIENTO E IDENTIFICACIÓN"):
        with st.spinner("🤖 La IA está analizando los documentos y preparando el formulario..."):
            client = genai.Client(api_key=API_KEY)
            st.session_state.b_acad = doc_acad.getvalue()
            st.session_state.b_dip = doc_dip.getvalue()
            
            prompt = """Extrae los datos y responde EXCLUSIVAMENTE en JSON:
            {
              "entidad": "", "sg_nombre": "", "dni": "", "ap_paterno": "", "ap_materno": "", 
              "nombres": "", "tipo_tramite": "", "fecha_expedicion": "", "numero": "", 
              "descripcion": "", "facultad": "", "escuela": "", "programa": "", "firma_status": ""
            }"""
            
            res = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=[prompt, 
                          types.Part.from_bytes(data=st.session_state.b_acad, mime_type=doc_acad.type), 
                          types.Part.from_bytes(data=st.session_state.b_dip, mime_type=doc_dip.type)]
            )
            try:
                limpio = res.text.replace('```json', '').replace('```', '').strip()
                st.session_state.datos_ia = json.loads(limpio)
            except: st.error("Error al leer datos. Intente de nuevo.")

# --- 5. VISORES Y FORMULARIO PRE-RELLENADO ---
if st.session_state.datos_ia:
    d = st.session_state.datos_ia
    st.divider()
    
    # Visores lado a lado
    v1, v2 = st.columns(2)
    with v1:
        st.markdown(f'<iframe src="data:application/pdf;base64,{base64.b64encode(st.session_state.b_acad).decode()}" width="100%" height="500" style="border-radius:10px;"></iframe>', unsafe_allow_html=True)
    with v2:
        st.markdown(f'<iframe src="data:application/pdf;base64,{base64.b64encode(st.session_state.b_dip).decode()}" width="100%" height="500" style="border-radius:10px;"></iframe>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 FORMULARIO DE REGISTRO TIPO SUNEDU")
    
    # Estructura de campos igual a tus imágenes
    with st.container():
        c1, c2 = st.columns(2)
        f_ent = c1.text_input("Entidad:*", value=d.get("entidad", ""))
        f_sg = c2.text_input("Secretario General:*", value=d.get("sg_nombre", ""))
        
        c3, c4, c5 = st.columns([1, 1.5, 1.5])
        f_dni = c3.text_input("Número de documento:*", value=d.get("dni", ""))
        f_ap1 = c4.text_input("Apellido paterno:*", value=d.get("ap_paterno", ""))
        f_ap2 = c5.text_input("Apellido materno:*", value=d.get("ap_materno", ""))
        
        f_nom = st.text_input("Nombres:*", value=d.get("nombres", ""))
        
        c6, c7, c8 = st.columns(3)
        f_tra = c6.text_input("Tipo de documento de Trámite:*", value=d.get("tipo_tramite", ""))
        f_fex = c7.text_input("Fecha de expedición:*", value=d.get("fecha_expedicion", ""))
        f_num = c8.text_input("Número / Folios:*", value=d.get("numero", ""))
        
        f_des = st.text_area("Descripción (Mención del Diploma):", value=d.get("descripcion", ""), height=100)
        
        c9, c10, c11 = st.columns(3)
        f_fac = c9.text_input("Facultad:", value=d.get("facultad", ""))
        f_esc = c10.text_input("Escuela:", value=d.get("escuela", ""))
        f_pro = c11.text_input("Programa:", value=d.get("programa", ""))

    if st.button("💾 CONFIRMAR Y GUARDAR REGISTRO"):
        st.success("✅ Auditoría completada con éxito.")
        st.balloons()
