from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
from app.config import (
    get_credentials, PROJECT_ID, EMBEDDING_MODEL, TOP_K_RESULTS,
    VERTEX_LOCATION, VECTOR_ENDPOINT_RESOURCE, VECTOR_DEPLOYED_INDEX_ID,
)
from app.embedding.vector_store import buscar
from app.embedding.chunk_store import buscar_textos
from app.geracao.gerador import gerar_resposta

_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def _init():
    aiplatform.init(
        project=PROJECT_ID, location=VERTEX_LOCATION,
        credentials=get_credentials(_SCOPES),
    )


def _embed_query(pergunta: str) -> list[float]:
    model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
    embedding = model.get_embeddings(
        [TextEmbeddingInput(text=pergunta, task_type="RETRIEVAL_QUERY")]
    )
    return embedding[0].values


def perguntar(pergunta: str) -> str:
    _init()

    query_embedding = _embed_query(pergunta)

    endpoint = aiplatform.MatchingEngineIndexEndpoint(VECTOR_ENDPOINT_RESOURCE)
    vizinhos = buscar(query_embedding, endpoint, VECTOR_DEPLOYED_INDEX_ID, TOP_K_RESULTS)

    ids = [v["id"] for v in vizinhos]
    textos = buscar_textos(ids)

    contextos = [textos[dp_id] for dp_id in ids if dp_id in textos]

    if not contextos:
        return "Não encontrei informações relevantes nos documentos para responder essa pergunta."

    return gerar_resposta(pergunta, contextos)
