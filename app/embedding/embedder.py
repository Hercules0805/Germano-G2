import time
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
from app.config import get_credentials, PROJECT_ID, EMBEDDING_MODEL, VERTEX_LOCATION

_BATCH_SIZE = 250
_TASK_TYPE = "RETRIEVAL_DOCUMENT"
_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def _init():
    aiplatform.init(
        project=PROJECT_ID, location=VERTEX_LOCATION,
        credentials=get_credentials(_SCOPES),
    )


def gerar_embeddings(chunks: list[dict]) -> list[dict]:
    _init()
    model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

    resultado = []
    total = len(chunks)

    for i in range(0, total, _BATCH_SIZE):
        batch = chunks[i: i + _BATCH_SIZE]
        inputs = [
            TextEmbeddingInput(text=c["texto"], task_type=_TASK_TYPE)
            for c in batch
        ]

        embeddings = model.get_embeddings(inputs)

        for chunk, emb in zip(batch, embeddings):
            resultado.append({**chunk, "embedding": emb.values})

        print(f"  Embeddings: {min(i + _BATCH_SIZE, total)}/{total}")

        if i + _BATCH_SIZE < total:
            time.sleep(1)

    return resultado
