import streamlit as st
from google import genai
from google.genai import types
import base64
import json

# --- 1. CONFIGURACIÓN ---
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"

# --- 2. LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema")
    with st.form("login"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u == USUARIO_CORRECTO and p == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Error")
    st.stop()

# --- 3. INTERFAZ DE CARGA ---
st.set_page_config(layout="wide")
st.title("🛡️ VERIFICADOR ACADÉMICO INTEGRAL")

col1, col2 = st.columns(2)
with col1:
    doc_acad = st.file_uploader("1. Subir Constancia Académica", type=['pdf', 'jpg', 'png'])
with col2:
    doc_dip = st.file_uploader("2. Subir Diploma", type=['pdf', 'jpg', 'png'])

# --- 4. PROCESAMIENTO E INTERFAZ TIPO SUNEDU ---
if doc_acad and doc_dip:
    client = genai.Client(api_key=API_KEY)
    
    with st.spinner("Transcribiendo datos al formulario..."):
        # Convertimos para la IA
        b_acad = doc_acad.getvalue()
        b_dip = doc_dip.getvalue()
        
        prompt = """Analiza y extrae los datos para este JSON:
        {
          "entidad": "", "sg_nombre": "", "dni": "", "ap_paterno": "", "ap_materno": "", 
          "nombres": "", "tipo_tramite": "", "fecha_expedicion": "", "numero": "", 
          "descripcion": "", "facultad": "", "escuela": "", "programa": ""
        }"""
        
        res = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[prompt, types.Part.from_bytes(data=b_acad, mime_type=doc_acad.type), 
                      types.Part.from_bytes(data=b_dip, mime_type=doc_dip.type)]
        )
        
        try:
            datos = json.loads(res.text.replace('```json', '').replace('```', '').strip())
        except:
            datos = {}

    st.divider()
    
    # VISORES
    v1, v2 = st.columns(2)
    with v1:
        st.markdown(f'<iframe src="data:application/pdf;base64,{base64.b64encode(b_acad).decode()}" width="100%" height="400"></iframe>', unsafe_allow_html=True)
    with v2:
        st.markdown(f'<iframe src="data:application/pdf;base64,{base64.b64encode(b_dip).decode()}" width="100%" height="400"></iframe>', unsafe_allow_html=True)

    # --- FORMULARIO ESTILO SUNEDU ---
    st.subheader("📋 Datos Extraídos (Editables)")
    
    # FILA 1
    c_ent, c_sg = st.columns(2)
    f_entidad = c_ent.text_input("Entidad:*", value=datos.get("entidad", ""))
    f_sg = c_sg.text_input("Secretario General:*", value=datos.get("sg_nombre", ""))
    
    # FILA 2
    c_dni, c_ap1, c_ap2 = st.columns([1, 1.5, 1.5])
    f_dni = c_dni.text_input("Número de documento:*", value=datos.get("dni", ""))
    f_ap1 = c_ap1.text_input("Apellido paterno:*", value=datos.get("ap_paterno", ""))
    f_ap2 = c_ap2.text_input("Apellido materno:*", value=datos.get("ap_materno", ""))
    
    # FILA 3
    f_nom = st.text_input("Nombres:*", value=datos.get("nombres", ""))
    
    # FILA 4
    c_tra, c_fex, c_num = st.columns(3)
    f_tra = c_tra.text_input("Tipo de Trámite:*", value=datos.get("tipo_tramite", ""))
    f_fex = c_fex.text_input("Fecha Expedición:*", value=datos.get("fecha_expedicion", ""))
    f_num = c_num.text_input("Número/Folios:*", value=datos.get("numero", ""))
    
    # FILA 5
    f_des = st.text_area("Descripción (Mención):", value=datos.get("descripcion", ""))
    
    # FILA 6
    c_fac, c_esc, c_pro = st.columns(3)
    f_fac = c_fac.text_input("Facultad:", value=datos.get("facultad", ""))
    f_esc = c_esc.text_input("Escuela:", value=datos.get("escuela", ""))
    f_pro = c_pro.text_input("Programa:", value=datos.get("programa", ""))

    if st.button("💾 Guardar y Finalizar"):
        st.success("¡Datos guardados!")
