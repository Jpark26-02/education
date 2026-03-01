import streamlit as st
from google import genai
from google.genai import types
import base64
import json
import time

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"

st.set_page_config(page_title="Auditoría SUNEDU", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "datos_ia" not in st.session_state:
    st.session_state.datos_ia = {}

# --- 2. LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema de Auditoría")
    with st.form("login"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u == USUARIO_CORRECTO and p == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Acceso denegado")
    st.stop()

# --- 3. CARGA DE DOCUMENTOS ---
st.title("🛡️ VERIFICADOR ACADÉMICO INTEGRAL (SUNEDU + SG)")
col_u1, col_u2 = st.columns(2)
with col_u1:
    doc_acad = st.file_uploader("1. DOCUMENTOS ACADÉMICOS", type=['pdf', 'jpg', 'png'])
with col_u2:
    doc_dip = st.file_uploader("2. DIPLOMAS", type=['pdf', 'jpg', 'png'])

# --- 4. PROCESAMIENTO AUTOMÁTICO ---
if doc_acad and doc_dip:
    if not st.session_state.datos_ia:
        with st.spinner("🤖 Analizando y transcribiendo datos..."):
            client = genai.Client(api_key=API_KEY)
            # Guardar bytes para visor
            st.session_state.b_acad = doc_acad.getvalue()
            st.session_state.b_dip = doc_dip.getvalue()
            
            prompt = """Extrae la info para SUNEDU y responde SOLO en JSON:
            {
              "entidad": "", "sg_nombre": "", "dni": "", "ap_paterno": "", "ap_materno": "", 
              "nombres": "", "tipo_tramite": "", "fecha_expedicion": "", "numero": "", 
              "descripcion": "", "facultad": "", "escuela": "", "programa": "", "firma_status": ""
            }"""
            
            try:
                res = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=[prompt, 
                              types.Part.from_bytes(data=st.session_state.b_acad, mime_type=doc_acad.type), 
                              types.Part.from_bytes(data=st.session_state.b_dip, mime_type=doc_dip.type)]
                )
                limpio = res.text.replace('```json', '').replace('```', '').strip()
                st.session_state.datos_ia = json.loads(limpio)
            except Exception as e:
                st.error(f"Error en IA: {e}")

# --- 5. VISORES Y FORMULARIO ---
if st.session_state.datos_ia:
    d = st.session_state.datos_ia
    st.divider()
    
    # Visores de PDF
    v1, v2 = st.columns(2)
    with v1:
        pdf_acad = base64.b64encode(st.session_state.b_acad).decode()
        st.markdown(f'<iframe src="data:application/pdf;base64,{pdf_acad}" width="100%" height="450"></iframe>', unsafe_allow_html=True)
    with v2:
        pdf_dip = base64.b64encode(st.session_state.b_dip).decode()
        st.markdown(f'<iframe src="data:application/pdf;base64,{pdf_dip}" width="100%" height="450"></iframe>', unsafe_allow_html=True)

    st.subheader("📋 FORMULARIO DE REGISTRO SUNEDU (Editable)")
    
    # Formulario con diseño de columnas similar a tus capturas
    with st.form("registro_sunedu"):
        c1, c2 = st.columns(2)
        f_ent = c1.text_input("Entidad:*", value=d.get("entidad", ""))
        f_sg = c2.text_input("Secretario General:*", value=d.get("sg_nombre", ""))
        
        c3, c4, c5 = st.columns([1, 1.5, 1.5])
        f_dni = c3.text_input("Número de documento:*", value=d.get("dni", ""))
        f_ap1 = c4.text_input("Apellido paterno:*", value=d.get("ap_paterno", ""))
        f_ap2 = c5.text_input("Apellido materno:*", value=d.get("ap_materno", ""))
        
        f_nom = st.text_input("Nombres:*", value=d.get("nombres", ""))
        
        c6, c7, c8 = st.columns(3)
        f_tra = c6.text_input("Tipo de Trámite:*", value=d.get("tipo_tramite", ""))
        f_fex = c7.text_input("Fecha de expedición:*", value=d.get("fecha_expedicion", ""))
        f_num = c8.text_input("Número/Folios:*", value=d.get("numero", ""))
        
        f_des = st.text_area("Descripción (Mención del Diploma):", value=d.get("descripcion", ""))
        
        c9, c10, c11 = st.columns(3)
        f_fac = c9.text_input("Facultad:", value=d.get("facultad", ""))
        f_esc = c10.text_input("Escuela:", value=d.get("escuela", ""))
        f_pro = c11.text_input("Programa:", value=d.get("programa", ""))

        if st.form_submit_button("💾 CONFIRMAR Y GUARDAR"):
            st.success("Auditoría Finalizada con Éxito")
