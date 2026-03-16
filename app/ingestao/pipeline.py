import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app.ingestao.conector import listar_arquivos, baixar_arquivo
from app.ingestao.parser import extrair_texto
from app.ingestao.chunker import fragmentar
from app.embedding.embedder import gerar_embeddings
from app.embedding.vector_store import criar_index, indexar_chunks


def executar_ingestao() -> list[dict]:
    print("Listando arquivos do Drive...")
    arquivos = listar_arquivos()
    print(f"{len(arquivos)} arquivo(s) encontrado(s).\n")

    todos_chunks = []

    for arq in arquivos:
        nome = arq["name"]
        file_id = arq["id"]
        mime_type = arq["mimeType"]

        print(f"Processando: {nome}")
        conteudo = baixar_arquivo(file_id, mime_type)
        texto = extrair_texto(conteudo, mime_type, nome)

        if not texto.strip():
            print(f"  [aviso] Sem texto extraído.\n")
            continue

        metadata = {
            "file_id": file_id,
            "nome": nome,
            "mime_type": mime_type,
            "modified_time": arq.get("modifiedTime"),
        }

        chunks = fragmentar(texto, metadata)
        todos_chunks.extend(chunks)
        print(f"  {len(chunks)} chunk(s) gerado(s).\n")

    print(f"Ingestão concluída: {len(todos_chunks)} chunks no total.")

    if not todos_chunks:
        return todos_chunks

    print("\nGerando embeddings...")
    chunks_com_embeddings = gerar_embeddings(todos_chunks)

    print("\nIndexando no Vertex AI Matching Engine...")
    index = criar_index()
    indexar_chunks(chunks_com_embeddings, index)
    print("Indexação concluída.")

    from app.embedding.chunk_store import salvar_chunks
    print("\nSalvando chunks no Firestore...")
    salvar_chunks(chunks_com_embeddings)

    return chunks_com_embeddings


if __name__ == "__main__":
    executar_ingestao()
