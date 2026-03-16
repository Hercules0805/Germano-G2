from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " ", ""],
)


def fragmentar(texto: str, metadata: dict) -> list[dict]:
    if not texto.strip():
        return []

    chunks = _splitter.split_text(texto)
    return [{"texto": chunk, "metadata": metadata} for chunk in chunks]
