import os
from dotenv import load_dotenv
import google.auth

load_dotenv()

_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def get_credentials(scopes: list[str] = None):
    if _CREDENTIALS_PATH and os.path.exists(_CREDENTIALS_PATH):
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(
            _CREDENTIALS_PATH, scopes=scopes,
        )
    creds, _ = google.auth.default(scopes=scopes)
    return creds


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

EMBEDDING_MODEL = "text-embedding-004"
LLM_MODEL = "gemini-2.5-pro"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5

VERTEX_LOCATION = "us-central1"
VECTOR_INDEX_RESOURCE = "projects/320234905146/locations/us-central1/indexes/6483945413320638464"
VECTOR_ENDPOINT_RESOURCE = "projects/320234905146/locations/us-central1/indexEndpoints/9223136741366431744"
VECTOR_DEPLOYED_INDEX_ID = "germano_g2_deployed"
