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

# --- 3. FUNCIÓN DE CONEXIÓN CORREGIDA (SCOPES EXACTOS) ---
def conectar_google_sheets():
    try:
        # Definición de Scopes EXACTA para evitar errores de Token
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Carga de credenciales desde los Secrets de Streamlit
        info_servicio = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(info_servicio, scopes=scope)
        cliente_g = gspread.authorize(creds)
        
        # Abre el archivo por su nombre exacto
        return cliente_g.open("Memoria_IA")
    except Exception as e:
        st.error(f"❌ Error de conexión a Google Sheets: {e}")
        return None

# --- 4. CONFIGURACIÓN DE PÁGINA PRINCIPAL ---
st.set_page_config(page_title="Auditoría Académica Pro", layout="wide", page_icon="🛡️")

# Barra lateral para navegación
st.sidebar.title("Opciones")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

st.title("🛡️ SISTEMA DE AUDITORÍA INTEGRAL (SG + MEMORIA)")

libro = conectar_google_sheets()

if libro:
    # Intentar cargar la Base de Datos de Secretarios Generales
    try:
        hoja_sg = libro.worksheet("Base_SG")
        df_sg = pd.DataFrame(hoja_sg.get_all_records())
        
        # Preparación de datos para la búsqueda
        df_sg['NOMBRE_COMPLETO'] = (df_sg['Nombres'] + " " + df_sg['Primer Apellido']).str.upper()
        df_sg['Fecha de Inicio'] = pd.to_datetime(df_sg['Fecha de Inicio'], errors='coerce')
        df_sg['Fecha de Fin'] = pd.to_datetime(df_sg['Fecha de Fin'], errors='coerce')
    except Exception as e:
        st.warning(f"⚠️ No se pudo cargar la pestaña 'Base_SG'. Verifica el nombre en el Excel.")
        df_sg = pd.DataFrame()

    # --- 5. CARGA Y PROCESAMIENTO ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📁 Carga de Expediente")
        constancia = st.file_uploader("Subir Constancia Maestra", type=['pdf', 'jpg', 'png'])
        anexos = st.file_uploader("Subir Anexos", type=['pdf', 'jpg', 'png'], accept_multiple_files=True)

    if constancia and anexos:
        try:
            client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})
            
            with st.spinner("🤖 IA analizando y validando datos..."):
                # Leer bytes del archivo para la IA
                bytes_data = constancia.getvalue()
                blob_c = types.Part.from_bytes(data=bytes_data, mime_type=constancia.type)
                
                prompt_auditoria = """
                Actúa como Auditor Académico. Analiza el documento y extrae:
                - UNIVERSIDAD: Nombre exacto.
                - SG: Nombre del Secretario General que firma.
                - FECHA: Fecha de emisión (DD/MM/AAAA).
                - TRAMITE: Tipo de grado o certificado.
                - EVALUACIÓN ANEXOS: Lista breve de anexos hallados.
                """
                
                response = client.models.generate_content(model="gemini-1.5-flash", contents=[prompt_auditoria, blob_c])
                res_ia = response.text.upper()
                
                with col2:
                    st.subheader("📋 Diagnóstico de la Auditoría")
                    st.code(res_ia)
                    
                    st.divider()
                    st.subheader("🧠 Entrenar Sistema")
                    correccion = st.text_input("Corrección (si la IA se equivocó):")
                    obs_anexos = st.text_area("Estado de los anexos:")
                    
                    if st.button("💾 Guardar y Aprender"):
                        try:
                            hoja_apr = libro.worksheet("Aprendizaje")
                            hoja_apr.append_row([
                                time.ctime(),
                                res_ia[:200],
                                "IA_AUDIT",
                                correccion if correccion else "VALIDADO",
                                obs_anexos if obs_anexos else "OK"
                            ])
                            st.success("✅ ¡Aprendido! Registro guardado en Google Sheets.")
                            st.balloons()
                        except:
                            st.error("❌ Error al escribir en la pestaña 'Aprendizaje'.")
        
        except Exception as e:
            st.error
