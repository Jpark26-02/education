response = client.models.generate_content(
    model="gemini-1.5-pro",
    contents=["Dime el nombre del secretario que firma este documento. Solo el nombre.", documento]
)

nombre_ia = response.text.strip().upper()
st.subheader(f"✍️ Detectado: {nombre_ia}")

match = df_base[df_base['NOMBRE_COMPLETO'].str.contains(nombre_ia, na=False, case=False)]

if not match.empty:
    mensaje_celeste = f"✅ REGISTRO CELESTE: {match['Universidad'].values[0]}"
    st.markdown(
        f'<div style="background-color: #00FFFF; padding: 20px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">{mensaje_celeste}</div>',
        unsafe_allow_html=True
    )
    st.balloons()
else:
    st.markdown(
        '<div style="background-color: #FF0000; padding: 20px; border-radius: 10px; color: white; text-align: center; font-weight: bold;">❌ REGISTRO ROJO: Autoridad no encontrada</div>',
        unsafe_allow_html=True
    )
