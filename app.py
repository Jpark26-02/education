import streamlit as st

# Configuración de seguridad simple
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "1234"

st.set_page_config(page_title="Verificador Privado")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Acceso Restringido")
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if user == USUARIO_CORRECTO and password == CLAVE_CORRECTA:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
else:
    st.title("📄 Verificador de Documentos")
    st.success("Sesión iniciada correctamente.")
    st.write("Sube tus documentos aquí para comenzar la verificación.")
    archivo = st.file_uploader("Selecciona un PDF o Imagen", type=["pdf", "jpg", "png"])
