import streamlit as st
import PyPDF2
from io import BytesIO

def unir_pdfs(lista_pdfs):
    """Une múltiples archivos PDF y devuelve el contenido en bytes."""
    merger = PyPDF2.PdfMerger()
    
    for pdf in lista_pdfs:
        merger.append(pdf)
    
    salida = BytesIO()
    merger.write(salida)
    merger.close()
    salida.seek(0)
    return salida

st.title("Unir PDFs")

cargados = st.file_uploader("Sube tus archivos PDF", type=["pdf"], accept_multiple_files=True)

if cargados:
    if st.button("Unir PDFs"):
        pdf_unido = unir_pdfs(cargados)
        st.download_button(
            label="Descargar PDF Unido",
            data=pdf_unido,
            file_name="pdf_unido.pdf",
            mime="application/pdf"
        )
