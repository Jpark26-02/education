import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time

# --- 1. CONFIGURACIÓN DE ACCESO Y SEGURIDAD ---
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"

try:
    client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})
except Exception as e:
    st.error(f"Error de conexión IA: {e}")

# --- 2. GESTIÓN DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "datos" not in st.session_state:
    st.session_state.datos = {}

# --- 3. LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Acceso Sistema Integral SG")
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u == USUARIO_CORRECTO and p == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    st.stop()

# --- 4. CARGA DE BASE DE DATOS (SG) ---
@st.cache_data
def cargar_base():
    try:
        df = pd.read_excel("secretarios.xlsx")
        df.columns = df.columns.str.strip()
        df['NOMBRE_COMPLETO'] = (df['Nombres'].astype(str) + " " + 
                                 df['Primer Apellido'].astype(str) + " " + 
                                 df['Segundo Apellido'].astype(str)).str.upper().str.strip()
        return df
    except:
        return None

df_base = cargar_base()

# --- 5. INTERFAZ PRINCIPAL ---
st.title("📘 SISTEMA INTEGRAL DE VERIFICACIÓN")
st.caption("Versión Final Gratuita - Control Académico")

archivo = st.file_uploader("1️⃣ Carga de Documento (PDF/Imagen)", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo:
    st.info("🔍 Procesando con Gemini IA y Reglas de Negocio...")
    
    try:
        with st.spinner("🤖 Analizando contenido..."):
            file_bytes = archivo.read()
            doc_part = types.Part.from_bytes(data=file_bytes, mime_type=archivo.type)
            
            # PROMPT CON REGLAS DE NEGOCIO (OCR + CLASIFICACIÓN)
            prompt_regras = """
            Actúa como un experto en control académico. Extrae:
            1. Nombre del estudiante. 2. DNI. 3. Carrera/Facultad. 4. Fecha de emisión.
            5. Nombre del Secretario General (SG). 6. ¿Es Notariado? (Sello/Firma notario).
            7. ¿Es Blanco y Negro?. 8. Tipo: Diploma o Documento Académico.
            Responde en formato clave: valor.
            """
            
            # CORRECCIÓN DE SINTAXIS (Línea 103 corregida)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[prompt_regras, doc_part]
            )
            
            res_text = response.text.upper()
            st.session_state.datos['raw'] = res_text

            # --- 7️⃣ OBSERVACIONES AUTOMÁTICAS ---
            st.subheader("📋 Resultados del Análisis")
            
            # Detección de Notariado (Regla 4)
            es_notario = any(x in res_text for x in ["NOTARÍA", "NOTARIO", "LEGALIZACIÓN", "FE NOTARIAL"])
            if es_notario:
                st.warning("📜 DOCUMENTO NOTARIADO")
            
            # Detección Blanco y Negro
            if "BLANCO Y NEGRO" in res_text or "MONOCROMÁTICO" in res_text:
                st.error("⚪ COPIA SIMPLE / IMAGEN BLANCO Y NEGRO")

            # Validación Secretario General (Rango Celeste/Rojo)
            # Extraemos un nombre simple para buscar (mejorar con Regex en producción)
            match_sg = None
