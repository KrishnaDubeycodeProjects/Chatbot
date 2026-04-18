import fitz  # PyMuPDF
import io

_ocr_reader = None

def get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        import easyocr
        print("🤖 Powering up EasyOCR Vision Model (this may take a few seconds)...")
        _ocr_reader = easyocr.Reader(['en'])
    return _ocr_reader

def parse_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extracts text from a sequence of PDF bytes using PyMuPDF (fitz), with an automatic Image OCR fallback."""
    extracted_text = ""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # STAGE 1: Attempt native text extraction
        for page in doc:
            extracted_text += page.get_text() + "\n"
            
        # If we successfully ripped standard text strings > 50 characters, we win!
        if len(extracted_text.strip()) > 50:
            doc.close()
            return extracted_text
            
        # STAGE 2: If we get here, the PDF is a flat scanned image. Activate OCR sequence.
        print("⚠️ No extractable native text detected! PDF is an image scan. Initializing OCR protocol...")
        extracted_text = ""
        reader = get_ocr_reader()
        
        for i, page in enumerate(doc):
            print(f"🔍 Reading visual text on Page {i+1}...")
            # Render the page to a PNG Image pixelmap in memory (150 DPI is a stable resolution for OCR)
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            
            # Feed the png to EasyOCR to detect mathematical lines of words
            result = reader.readtext(img_bytes, detail=0)
            extracted_text += " ".join(result) + "\n"
            
        doc.close()
    except Exception as e:
        print(f"⚠️ PDF extraction process failed entirely: {e}")
        
    return extracted_text
