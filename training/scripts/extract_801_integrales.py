"""
Script para extraer el contenido del PDF 801_Integrales
y guardarlo como texto plano para posterior procesamiento.
"""

import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF no esta instalado. Ejecuta: pip install PyMuPDF")
    sys.exit(1)


PDF_PATH = Path(r"C:\Users\LOQ\Downloads\801_Integrales.pdf")
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "801_integrales_raw.txt"


def extract_pdf(pdf_path: Path, output_path: Path) -> None:
    if not pdf_path.exists():
        print(f"Error: No se encontro el archivo {pdf_path}")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    print(f"PDF abierto: {pdf_path.name}")
    print(f"Total de paginas: {total_pages}")
    print(f"Extrayendo texto...")

    full_text = []
    pages_with_text = 0
    pages_empty = 0

    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text("text").strip()

        if text:
            pages_with_text += 1
            full_text.append(f"{'='*60}")
            full_text.append(f"PAGINA {page_num + 1}")
            full_text.append(f"{'='*60}")
            full_text.append(text)
            full_text.append("")
        else:
            pages_empty += 1

    doc.close()

    content = "\n".join(full_text)
    output_path.write_text(content, encoding="utf-8")

    print(f"\nResumen:")
    print(f"  Paginas con texto: {pages_with_text}")
    print(f"  Paginas vacias/escaneadas: {pages_empty}")
    print(f"  Archivo generado: {output_path}")
    print(f"  Tamano: {output_path.stat().st_size / 1024:.1f} KB")

    if pages_empty > pages_with_text:
        print(f"\n⚠ ADVERTENCIA: La mayoria de paginas no tienen texto extraible.")
        print(f"  El PDF probablemente es escaneado. Se necesitara OCR.")

    # Mostrar preview de las primeras lineas
    preview_lines = content.split("\n")[:30]
    print(f"\nPreview (primeras 30 lineas):")
    print("-" * 40)
    for line in preview_lines:
        print(line)


if __name__ == "__main__":
    extract_pdf(PDF_PATH, OUTPUT_FILE)
