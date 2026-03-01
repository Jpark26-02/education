import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import re
from PIL import Image
import io

# --- 1. CONFIGURACIÓN DE ACCESO Y LLAVE ---
API_KEY = "AIzaSyAKJmu6ooG5-1uEyubIJbRiEAnRdIjYxwU"
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "educacion2026"

try:
    client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})
except Exception as e:
    st.error(f"Error de conexión con Gemini: {e}")

# --- 2. ESTADO DE LA SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "datos_extraidos" not in st.session_state:
    st.session_state.datos_extraidos = None

# --- 3. FUNCIÓN DE LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema Integral")
    with st.form("login"):
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
def cargar_base_sg():
    try:
        df = pd.read_excel("secretarios.xlsx")
        df.columns = df.columns.str.strip()
        # Crear nombre completo para búsqueda
        df['NOMBRE_COMPLETO'] = (df['Nombres'].fillna('') + " " + 
                                 df['Primer Apellido'].fillna('') + " " + 
                                 df['Segundo Apellido'].fillna('')).str.upper().str.strip()
        return df
    except:
        st.warning("⚠️ No se detectó 'secretarios.xlsx'. La validación de SG será limitada.")
        return None

df_sg = cargar_base_sg()

# --- 5. INTERFAZ PRINCIPAL ---
st.title("📘 SISTEMA INTEGRAL DE VERIFICACIÓN")
st.sidebar.header("Opciones")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

# 1️⃣ CLASIFICACIÓN Y CARGA
st.header("1️⃣ Carga de Documento")
archivo = st.file_uploader("Sube el Diploma o Documento Académico", type=['pdf', 'jpg', 'png', 'jpeg'])

if archivo:
    st.info("🔍 Procesando con OCR Tesseract y Gemini IA...")
    
    try:
        file_bytes = archivo.read()
        
        # Simulación de detección de Copia Simple (Blanco y Negro)
        # (En una versión avanzada se usaría OpenCV, aquí lo inferimos por el prompt)
        
        with st.spinner("🤖 Analizando reglas de validación..."):
            documento_part = types.Part.from_bytes(data=file_bytes, mime_type=archivo.type)
            
            # PROMPT INTEGRAL con todas tus reglas
            prompt = """
            Analiza este documento y extrae la siguiente estructura JSON:
            {
              "nombre_estudiante": "",
              "dni": "",
              "tipo_documento": "Diploma / Académico no diploma / No académico",
              "carrera": "",
              "universidad": "",
              "fecha_emision": "",
              "fecha_firma_sg": "",
              "nombre_sg": "",
              "es_notariado": false,
              "es_blanco_negro": false,
              "tiene_firma_digital": false
            }
            Reglas: Si es Diploma y no hay fecha de firma, usa la de emisión. 
            Si es Académico no diploma y no hay emisión, usa la del SG.
            Detecta palabras como 'Notaría' o 'Sello Notarial'.
            """
            
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[prompt,
