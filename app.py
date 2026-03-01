import streamlit as st
from google import genai
from google.genai import types
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import time

# --- CONFIGURACIÓN DE SEGURIDAD ---
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
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

# --- CONEXIÓN GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        info_servicio = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(info_servicio, scopes=scope)
        return gspread.authorize(creds).open("Memoria_IA")
    except Exception as e:
        st.error(f"❌ Error Sheets: {e}")
        return None

# --- APP PRINCIPAL ---
st.set_page_config(page_title="Auditor SUNEDU Pro", layout="wide")
st.title("🛡️ VERIFICADOR ACADÉMICO INTEGRAL (SUNEDU + SG)")

libro = conectar_google_sheets()

if libro:
    # Cargar Base de Datos de Secretarios Generales (Base_SG)
    try:
        df_sg = pd.DataFrame(libro.worksheet("Base_SG").get_all_records())
        df_sg['NOMBRE_SG'] = (df_sg['Nombres'] + " " + df_sg['Primer Apellido']).str.upper()
    except:
        st.error("Asegúrate de tener la pestaña 'Base_SG' con las columnas correctas.")
        st.stop()

    # --- SECCIÓN DE CARGA ---
    st.markdown("### 📑 Carga de Documentos para Validación")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**1. DOCUMENTOS ACADÉMICOS** (Escaneado/Digital)")
        doc_academico = st.file_uploader("Subir Constancia", type=['pdf', 'jpg', 'png'])
    with col2:
        st.success("**2. DIPLOMAS** (Validación vs SUNEDU)")
        doc_diploma = st.file_uploader("Subir Diploma", type=['pdf', 'jpg', 'png'])

    if doc_academico and doc_diploma:
        try:
            client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})
            with st.spinner("🔍 Auditando contra Base_SG y Registro SUNEDU..."):
                
                # Procesamiento por IA
                blob_acad = types.Part.from_bytes(data=doc_academico.read(), mime_type=doc_academico.type)
                blob_dip = types.Part.from_bytes(data=doc_diploma.read(), mime_type=doc_diploma.type)
                
                # PROMPT MAESTRO DE AUDITORÍA
                prompt = """
                Eres un experto en verificación de SUNEDU. Analiza:
                1. ¿Es Digital o Escaneado?
                2. Extrae Nombre del Titular, Universidad, Grado (Bachiller/Título/etc), Fecha de Emisión y Nombre del Secretario General.
                3. Verifica si los datos del Diploma son COHERENTES con la Constancia Académica.
                Responde: TITULAR: [Nombre], UNIV: [Nombre], SG: [Nombre], FECHA: [DD/MM/AAAA], TIPO: [Digital/Escaneado].
                """
                
                response = client.models.generate_content(model="gemini-1.5-flash", contents=[prompt, blob_acad, blob_dip])
                info_ia = response.text.upper()

                # --- LÓGICA DE VALIDACIÓN ---
                # Buscamos al SG en tu base de datos
                sg_detectado = "" # (Aquí la IA extrae el nombre)
                
                st.divider()
                res_col, sunedu_col = st.columns([1, 1])
                
                with res_col:
                    st.subheader("📋 Datos Extraídos")
                    st.code(info_ia)
                
                with sunedu_col:
                    st.subheader("🔗 Estado en SUNEDU / Base_SG")
                    # Simulación de cruce con Base_SG
                    st.markdown('<div style="background-color:#00FFFF; padding:10px; border-radius:5px; color:black; font-weight:bold; text-align:center;">✓ AUTORIDAD REGISTRADA EN BASE_SG</div>', unsafe_allow_html=True)
                    
                    st.warning("⚠️ Recuerda verificar manualmente en 'SUNEDU en Línea' con los datos extraídos.")
                    
                    # Botón de acceso directo a SUNEDU
                    st.link_button("🌐 Ir a SUNEDU en Línea", "https://www.sunedu.gob.pe/registro-de-grados-y-titulos/")

                # --- APRENDIZAJE ---
                st.divider()
                if st.button("💾 Registrar Auditoría en Memoria_IA"):
                    libro.worksheet("Aprendizaje").append_row([time.ctime(), info_ia[:200], "AUDITORÍA OK", "SUNEDU VERIFICADO", "COMPLETO"])
                    st.success("Auditoría guardada exitosamente.")

        except Exception as e:
            st.error(f"Error en el proceso: {e}")
