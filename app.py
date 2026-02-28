import streamlit as st
import time
import pandas as pd

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="SISTEMA INTEGRAL DE VERIFICACIÓN", layout="wide")

# Inicializar sesión para edición manual (Punto 6)
if 'datos_doc' not in st.session_state:
    st.session_state.datos_doc = {
        "nombre": "", "dni": "", "carrera": "", "fecha_emision": "", "observaciones": []
    }

st.title("📘 Sistema Integral de Verificación Académica")

# --- 1️⃣ CLASIFICACIÓN Y CARGA (Punto 1) ---
with st.sidebar:
    st.header("Configuración de Carga")
    tipo_doc = st.selectbox("Tipo de Documento", 
        ["Diploma", "Certificado/Constancia", "Documento Notariado", "No Académico"])
    formato = st.radio("Formato", ["PDF Digital Nativo", "Escaneo/Foto", "Copia B/N"])

archivo = st.file_uploader("Subir documento para proceso OCR y IA", type=['pdf', 'png', 'jpg'])

if archivo:
    # Simulación de proceso OCR (Punto 2)
    with st.spinner("Ejecutando Tesseract OCR y Análisis Gemini..."):
        time.sleep(2) # Simulación de proceso
        st.session_state.datos_doc["nombre"] = "JUAN PEREZ GARCIA" # Ejemplo extraído
        st.session_state.datos_doc["carrera"] = "INGENIERÍA DE SISTEMAS"

    # --- 3️⃣ & 6️⃣ PANEL DE RESULTADOS Y EDICIÓN ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 Datos Extraídos (Editables)")
        nombre = st.text_input("Nombre del Interesado", st.session_state.datos_doc["nombre"])
        carrera = st.text_input("Mención/Carrera", st.session_state.datos_doc["carrera"])
        
        if st.button("✏️ Guardar y Revalidar Manualmente"):
            st.toast("Datos actualizados. Revalidando con base de SG...")

    with col2:
        st.subheader("🚩 Observaciones Automáticas (Punto 7)")
        # Lógica de reglas (Punto 4)
        if formato == "Escaneo/Foto":
            st.error("⚠️ FIRMA ELECTRÓNICA NO VALIDADA (Escaneo detectado)")
        if tipo_doc == "Documento Notariado":
            st.info("ℹ️ DOCUMENTO NOTARIADO")
        
        # Simulación validación SUNEDU (Punto 5)
        if st.button("Consultar SUNEDU"):
            st.warning("Esperando 10 segundos para verificación 'No soy un robot'...")
            time.sleep(10)
            st.success("Coincidencia total encontrada en SUNEDU")

    # --- 1️⃣1️⃣ ESTADO FINAL ---
    st.divider()
    st.subheader("Estado Final del Documento")
    st.markdown("### ✅ VÁLIDO CON OBSERVACIONES")
