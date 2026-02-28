import streamlit as st
import google.generativeai as genai
import pytesseract
from PIL import Image

# Esto busca la clave que guardaste en Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Falta la configuración de la API Key en Secrets.")

model = genai.GenerativeModel('gemini-1.5-flash')

# ... resto de tu código del Verificador ...
