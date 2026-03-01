@st.cache_data
def cargar_base_excel():
    try:
        df = pd.read_excel("secretarios.xlsx")
        
        # LIMPIEZA DE COLUMNAS: Elimina espacios y pasa todo a mayúsculas
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Creamos el nombre completo usando los nombres exactos detectados
        # Buscamos las columnas aunque tengan nombres ligeramente distintos
        col_nombres = 'NOMBRES'
        col_ape1 = 'PRIMER APELLIDO'
        col_ape2 = 'SEGUNDO APELLIDO'

        df['nombre_completo'] = (
            df[col_nombres].astype(str) + " " + 
            df[col_ape1].astype(str) + " " + 
            df[col_ape2].astype(str)
        ).str.upper().str.strip()
        
        return df
    except KeyError as e:
        st.error(f"No se encontró la columna: {e}. Revisa que en tu Excel las columnas se llamen exactamente: Nombres, Primer Apellido, Segundo Apellido.")
        return None
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return None
