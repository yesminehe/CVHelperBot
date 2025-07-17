import pdfplumber
from typing import Union, IO

def extract_text_from_pdf(file: Union[str, IO]) -> str:
    """
    Extract text from a PDF file or file-like object.
    Args:
        file (str or file-like): Path to the PDF file or a file-like object.
    Returns:
        str: Extracted text from the PDF, preserving spaces and line breaks.
    """
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=1, y_tolerance=1)
            if page_text:
                text += page_text + "\n"
    return text
