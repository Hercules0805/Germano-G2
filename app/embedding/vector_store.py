import time
import uuid
from google.cloud import aiplatform
from app.config import get_credentials, PROJECT_ID, VERTEX_LOCATION

_DIMENSIONS = 768
_INDEX_DISPLAY_NAME = "germano-g2-index"
_ENDPOINT_DISPLAY_NAME = "germano-g2-endpoint"
_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def _init():
    aiplatform.init(
        project=PROJECT_ID, location=VERTEX_LOCATION,
        credentials=get_credentials(_SCOPES),
    )


def criar_index() -> aiplatform.MatchingEngineIndex:
    _init()

    indexes = aiplatform.MatchingEngineIndex.list(
        filter=f'display_name="{_INDEX_DISPLAY_NAME}"'
    )
    if indexes:
        print(f"Index já existe: {indexes[0].resource_name}")
        return indexes[0]

    index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=_INDEX_DISPLAY_NAME,
        dimensions=_DIMENSIONS,
        approximate_neighbors_count=150,
        distance_measure_type="DOT_PRODUCT_DISTANCE",
        index_update_method="STREAM_UPDATE",
        leaf_node_embedding_count=500,
        leaf_nodes_to_search_percent=7,
    )
    print(f"Index criado: {index.resource_name}")
    return index


def criar_endpoint() -> aiplatform.MatchingEngineIndexEndpoint:
    _init()

    endpoints = aiplatform.MatchingEngineIndexEndpoint.list(
        filter=f'display_name="{_ENDPOINT_DISPLAY_NAME}"'
    )
    if endpoints:
        print(f"Endpoint já existe: {endpoints[0].resource_name}")
        return endpoints[0]

    endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=_ENDPOINT_DISPLAY_NAME,
        public_endpoint_enabled=True,
    )
    print(f"Endpoint criado: {endpoint.resource_name}")
    return endpoint


def indexar_chunks(chunks_com_embeddings: list[dict], index: aiplatform.MatchingEngineIndex):
    datapoints = []
    for chunk in chunks_com_embeddings:
        dp_id = str(uuid.uuid4())
        chunk["datapoint_id"] = dp_id
        datapoints.append({
            "datapoint_id": dp_id,
            "feature_vector": chunk["embedding"],
        })

    BATCH = 100
    for i in range(0, len(datapoints), BATCH):
        batch = datapoints[i: i + BATCH]
        index.upsert_datapoints(datapoints=batch)
        print(f"  Indexados: {min(i + BATCH, len(datapoints))}/{len(datapoints)}")
        time.sleep(0.5)


def buscar(
    query_embedding: list[float],
    endpoint: aiplatform.MatchingEngineIndexEndpoint,
    deployed_index_id: str,
    top_k: int = 5,
) -> list[dict]:
    resp = endpoint.find_neighbors(
        deployed_index_id=deployed_index_id,
        queries=[query_embedding],
        num_neighbors=top_k,
    )
    if not resp or not resp[0]:
        return []
    return [
        {"id": n.id, "distancia": n.distance}
        for n in resp[0]
    ]
