import streamlit as st
from pypdf import PdfWriter, PdfReader
from io import BytesIO

st.set_page_config(page_title="Unir PDFs", page_icon="📄")
st.title("📄 Unir PDFs")

# --- Inicializar estado ---
if "archivos" not in st.session_state:
    st.session_state.archivos = []

# --- Cargar archivos ---
nuevos = st.file_uploader(
    "Sube tus archivos PDF",
    type=["pdf"],
    accept_multiple_files=True,
    key="uploader",
)

# Agregar nuevos archivos evitando duplicados por nombre
if nuevos:
    nombres_existentes = {a.name for a in st.session_state.archivos}
    for f in nuevos:
        if f.name not in nombres_existentes:
            st.session_state.archivos.append(f)

# --- Lista de archivos con botón eliminar ---
if st.session_state.archivos:
    st.subheader(f"Archivos cargados ({len(st.session_state.archivos)})")

    for i, archivo in enumerate(st.session_state.archivos):
        col1, col2, col3 = st.columns([0.6, 0.25, 0.15])
        col1.markdown(f"📎 **{archivo.name}**")
        size_kb = round(len(archivo.getvalue()) / 1024, 1)
        col2.caption(f"{size_kb} KB")
        if col3.button("🗑️ Eliminar", key=f"del_{i}_{archivo.name}"):
            st.session_state.archivos.pop(i)
            st.rerun()

    st.divider()

    # --- Opción de compresión ---
    comprimir = st.checkbox(
        "🗜️ Comprimir PDF resultante",
        value=False,
        help="Reduce el tamaño eliminando datos duplicados y comprimiendo el contenido.",
    )

    nivel_compresion = 0
    if comprimir:
        nivel_compresion = st.select_slider(
            "Nivel de compresión",
            options=[1, 2, 3, 4, 5, 6, 7, 8, 9],
            value=6,
            format_func=lambda x: {
                1: "1 – Mínima",
                2: "2",
                3: "3",
                4: "4",
                5: "5 – Media",
                6: "6 – Recomendada",
                7: "7",
                8: "8",
                9: "9 – Máxima",
            }[x],
        )

    # --- Botón unir ---
    if st.button("✅ Unir PDFs", type="primary", use_container_width=True):
        with st.spinner("Procesando..."):
            writer = PdfWriter()

            for pdf_file in st.session_state.archivos:
                pdf_file.seek(0)
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)

            if comprimir:
                for page in writer.pages:
                    page.compress_content_streams(level=nivel_compresion)

            salida = BytesIO()
            writer.write(salida)
            salida.seek(0)

        tamanio_kb = round(len(salida.getvalue()) / 1024, 1)
        st.success(f"PDF listo — {tamanio_kb} KB")

        st.download_button(
            label="⬇️ Descargar PDF Unido",
            data=salida,
            file_name="pdf_unido.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
else:
    st.info("Sube uno o más archivos PDF para comenzar.")
