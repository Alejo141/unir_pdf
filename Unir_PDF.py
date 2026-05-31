import streamlit as st
import PyPDF2
from io import BytesIO
import subprocess
import tempfile
import os

st.set_page_config(page_title="Unir PDFs", page_icon="📄")
st.title("📄 Unir PDFs")

def unir_pdfs(lista_pdfs):
    merger = PyPDF2.PdfMerger()
    for pdf in lista_pdfs:
        pdf.seek(0)
        merger.append(pdf)
    buf = BytesIO()
    merger.write(buf)
    merger.close()
    buf.seek(0)
    return buf.read()

def comprimir_con_ghostscript(datos_pdf, perfil):
    """Comprime usando Ghostscript. Perfiles de menor a mayor compresión:
       screen < ebook < printer < prepress
    """
    with tempfile.TemporaryDirectory() as tmp:
        entrada = os.path.join(tmp, "entrada.pdf")
        salida  = os.path.join(tmp, "salida.pdf")

        with open(entrada, "wb") as f:
            f.write(datos_pdf)

        cmd = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS=/{perfil}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dCompressFonts=true",
            "-dSubsetFonts=true",
            "-dDetectDuplicateImages=true",
            "-dColorImageDownsampleType=/Bicubic",
            "-dGrayImageDownsampleType=/Bicubic",
            "-dMonoImageDownsampleType=/Bicubic",
            f"-sOutputFile={salida}",
            entrada,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0 or not os.path.exists(salida):
            return None, result.stderr

        with open(salida, "rb") as f:
            return f.read(), None

# --- Upload ---
cargados = st.file_uploader(
    "Sube tus archivos PDF",
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if cargados:
    st.caption(f"✅ {len(cargados)} archivo(s) cargado(s)")
    st.divider()

    comprimir = st.checkbox("🗜️ Comprimir PDF resultante", value=True)

    perfil_gs = "screen"
    if comprimir:
        perfil_gs = st.select_slider(
            "Nivel de compresión",
            options=["prepress", "printer", "ebook", "screen"],
            value="screen",
            format_func=lambda x: {
                "prepress": "Mínima – alta calidad (prepress)",
                "printer":  "Media – impresión (printer)",
                "ebook":    "Alta – pantalla HD (ebook)",
                "screen":   "Máxima – pantalla baja res (screen)",
            }[x],
        )
        st.caption({
            "prepress": "🖨️ Ideal para imprenta. Mínima reducción.",
            "printer":  "📄 Buena calidad, algo de reducción.",
            "ebook":    "📱 Balance ideal: buena imagen, buen tamaño.",
            "screen":   "💾 Máxima compresión. Recomendado para compartir por correo/web.",
        }[perfil_gs])

    if st.button("✅ Unir PDFs", type="primary", use_container_width=True):
        with st.spinner("Uniendo archivos..."):
            datos_unidos = unir_pdfs(cargados)
            tamanio_orig = sum(len(f.getvalue()) for f in cargados)

        if comprimir:
            with st.spinner("Comprimiendo con Ghostscript..."):
                datos_finales, error = comprimir_con_ghostscript(datos_unidos, perfil_gs)

            if error or datos_finales is None:
                st.warning("⚠️ Ghostscript no disponible. Descargando sin compresión extra.")
                datos_finales = datos_unidos
        else:
            datos_finales = datos_unidos

        tamanio_final = len(datos_finales)
        reduccion = round((1 - tamanio_final / tamanio_orig) * 100, 1) if tamanio_orig else 0

        col1, col2 = st.columns(2)
        col1.metric("Tamaño original", f"{round(tamanio_orig/1024,1)} KB")
        col2.metric(
            "Tamaño final",
            f"{round(tamanio_final/1024,1)} KB",
            delta=f"-{reduccion}%" if reduccion > 0 else "Sin reducción",
            delta_color="inverse",
        )

        st.download_button(
            label="⬇️ Descargar PDF Unido",
            data=datos_finales,
            file_name="pdf_unido.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
else:
    st.info("Sube uno o más archivos PDF para comenzar.")
