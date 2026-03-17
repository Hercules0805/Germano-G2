from google.cloud import firestore
from app.config import get_credentials, PROJECT_ID

_COLLECTION = "chunks"
_COLLECTION_INDEXADOS = "arquivos_indexados"
_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def _get_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID, credentials=get_credentials(_SCOPES))


def salvar_chunks(chunks: list[dict]):
    db = _get_client()
    batch = db.batch()

    for i, chunk in enumerate(chunks):
        dp_id = chunk.get("datapoint_id")
        if not dp_id:
            continue
        doc_ref = db.collection(_COLLECTION).document(dp_id)
        batch.set(doc_ref, {
            "texto": chunk["texto"],
            "metadata": chunk.get("metadata", {}),
        })
        # Firestore batch limit = 500
        if (i + 1) % 500 == 0:
            batch.commit()
            batch = db.batch()

    batch.commit()
    print(f"  {len(chunks)} chunk(s) salvos no Firestore.")


def listar_indexados() -> set[str]:
    db = _get_client()
    docs = db.collection(_COLLECTION_INDEXADOS).stream()
    return {doc.id for doc in docs}


def marcar_indexado(file_id: str, nome: str):
    db = _get_client()
    db.collection(_COLLECTION_INDEXADOS).document(file_id).set({
        "nome": nome,
        "indexado_em": firestore.SERVER_TIMESTAMP,
    })


def buscar_textos(datapoint_ids: list[str]) -> dict[str, str]:
    if not datapoint_ids:
        return {}
    db = _get_client()
    refs = [db.collection(_COLLECTION).document(dp_id) for dp_id in datapoint_ids]
    docs = db.get_all(refs)
    return {doc.id: doc.to_dict()["texto"] for doc in docs if doc.exists}
