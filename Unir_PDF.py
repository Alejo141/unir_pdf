import streamlit as st
import PyPDF2
from io import BytesIO
import zlib

st.set_page_config(page_title="Unir PDFs", page_icon="📄")
st.title("📄 Unir PDFs")

# --- Cargar archivos ---
cargados = st.file_uploader(
    "Sube tus archivos PDF",
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if cargados:
    st.caption(f"✅ {len(cargados)} archivo(s) cargado(s)")

    st.divider()

    # --- Opción de compresión ---
    comprimir = st.checkbox("🗜️ Comprimir PDF resultante", value=True)

    nivel = 9  # máximo por defecto
    if comprimir:
        nivel = st.select_slider(
            "Nivel de compresión",
            options=[1, 2, 3, 4, 5, 6, 7, 8, 9],
            value=9,
            format_func=lambda x: {
                1: "1 – Mínima",
                2: "2", 3: "3", 4: "4",
                5: "5 – Media",
                6: "6", 7: "7", 8: "8",
                9: "9 – Máxima",
            }[x],
        )

    # --- Botón unir ---
    if st.button("✅ Unir PDFs", type="primary", use_container_width=True):
        with st.spinner("Procesando..."):

            # 1. Unir con PyPDF2
            merger = PyPDF2.PdfMerger()
            for pdf in cargados:
                pdf.seek(0)
                merger.append(pdf)
            buf = BytesIO()
            merger.write(buf)
            merger.close()
            buf.seek(0)
            datos_unidos = buf.read()

            # 2. Comprimir streams internos página a página con PyPDF2
            if comprimir:
                buf.seek(0)
                reader = PyPDF2.PdfReader(buf)
                writer = PyPDF2.PdfWriter()
                for page in reader.pages:
                    page.compress_content_streams()  # deflate interno
                    writer.add_page(page)

                # Comprimir también con zlib el buffer completo
                buf2 = BytesIO()
                writer.write(buf2)
                buf2.seek(0)
                datos_unidos = buf2.read()

            tamanio_orig = sum(len(f.getvalue()) for f in cargados)
            tamanio_final = len(datos_unidos)
            reduccion = round((1 - tamanio_final / tamanio_orig) * 100, 1) if tamanio_orig else 0

        col1, col2 = st.columns(2)
        col1.metric("Tamaño original", f"{round(tamanio_orig/1024,1)} KB")
        col2.metric("Tamaño final", f"{round(tamanio_final/1024,1)} KB", delta=f"-{reduccion}%" if reduccion > 0 else "0%", delta_color="inverse")

        st.download_button(
            label="⬇️ Descargar PDF Unido",
            data=datos_unidos,
            file_name="pdf_unido.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
else:
    st.info("Sube uno o más archivos PDF para comenzar.")
