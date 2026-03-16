import io
import csv
from pypdf import PdfReader


def extrair_texto(conteudo: bytes, mime_type: str, nome: str) -> str:
    try:
        if mime_type == "application/pdf":
            return _parse_pdf(conteudo)

        if mime_type in ("text/plain", "text/csv", "text/html"):
            return conteudo.decode("utf-8", errors="ignore")

        if mime_type in (
            "application/vnd.google-apps.document",
            "application/vnd.google-apps.presentation",
        ):
            return conteudo.decode("utf-8", errors="ignore")

        if mime_type in (
            "application/vnd.google-apps.spreadsheet",
            "application/vnd.ms-excel",
            "application/vnd.ms-excel.sheet.macroenabled.12",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ):
            return _parse_csv(conteudo)

        return ""
    except Exception as e:
        print(f"[parser] Erro em '{nome}': {e}")
        return ""


def _parse_pdf(conteudo: bytes) -> str:
    reader = PdfReader(io.BytesIO(conteudo))
    return "\n".join(
        page.extract_text() or "" for page in reader.pages
    )


def _parse_csv(conteudo: bytes) -> str:
    texto = conteudo.decode("utf-8", errors="ignore")
    reader = csv.reader(io.StringIO(texto, newline=""))
    return "\n".join(" | ".join(row) for row in reader)
