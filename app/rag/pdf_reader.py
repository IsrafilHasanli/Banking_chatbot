import os
from pypdf import PdfReader


def load_pdfs(folder_path: str):
    documents = []

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(folder_path, file))

            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""

            documents.append({
                "text": text,
                "source": file
            })

    return documents