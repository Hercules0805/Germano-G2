import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app.ingestao.conector import listar_arquivos, baixar_arquivo
from app.ingestao.parser import extrair_texto
from app.ingestao.chunker import fragmentar
from app.embedding.embedder import gerar_embeddings
from app.embedding.vector_store import criar_index, indexar_chunks
from app.embedding.chunk_store import salvar_chunks, listar_indexados, marcar_indexado


def executar_ingestao(limit: int = None) -> list[dict]:
    print("Listando arquivos do Drive...")
    arquivos = listar_arquivos()
    total_drive = len(arquivos)

    print("Consultando arquivos já indexados...")
    indexados = listar_indexados()
    arquivos = [a for a in arquivos if a["id"] not in indexados]
    print(f"{len(arquivos)} pendente(s) de {total_drive} no Drive ({len(indexados)} já indexado(s)).\n")

    if limit:
        arquivos = arquivos[:limit]
        print(f"Limitando a {limit} arquivo(s) nesta execução.\n")

    if not arquivos:
        print("Nada a processar.")
        return []

    index = criar_index()
    todos_chunks = []

    for i, arq in enumerate(arquivos, 1):
        nome = arq["name"]
        file_id = arq["id"]
        mime_type = arq["mimeType"]

        print(f"[{i}/{len(arquivos)}] {nome}")

        try:
            conteudo = baixar_arquivo(file_id, mime_type)
            texto = extrair_texto(conteudo, mime_type, nome)

            if not texto.strip():
                print("  [aviso] Sem texto extraído, pulando.\n")
                marcar_indexado(file_id, nome)
                continue

            metadata = {
                "file_id": file_id,
                "nome": nome,
                "mime_type": mime_type,
                "modified_time": arq.get("modifiedTime"),
            }

            chunks = fragmentar(texto, metadata)
            print(f"  {len(chunks)} chunk(s) gerado(s).")

            chunks_com_emb = gerar_embeddings(chunks)
            indexar_chunks(chunks_com_emb, index)
            salvar_chunks(chunks_com_emb)
            marcar_indexado(file_id, nome)

            todos_chunks.extend(chunks_com_emb)
            print(f"  Concluído.\n")

        except Exception as e:
            print(f"  [ERRO] {e}\n")
            continue

    print(f"Ingestão finalizada: {len(todos_chunks)} chunks processados nesta execução.")
    return todos_chunks


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Máx. de arquivos a processar")
    args = parser.parse_args()
    executar_ingestao(limit=args.limit)
