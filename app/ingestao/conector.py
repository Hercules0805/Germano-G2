import google.auth.transport.requests
from googleapiclient.discovery import build
from googleapiclient._auth import authorized_http
from app.config import get_credentials, DRIVE_FOLDER_ID

_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

SUPPORTED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.spreadsheet",
    "application/vnd.google-apps.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/vnd.ms-excel.sheet.macroenabled.12",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/csv",
    "text/plain",
]


def _build_service():
    creds = get_credentials(_SCOPES)
    creds.refresh(google.auth.transport.requests.Request())
    return build("drive", "v3", credentials=creds)


def listar_arquivos(folder_id: str = None) -> list[dict]:
    service = _build_service()
    folder_id = folder_id or DRIVE_FOLDER_ID
    drive_id = DRIVE_FOLDER_ID

    mime_filter = " or ".join(
        [f"mimeType='{m}'" for m in SUPPORTED_MIME_TYPES]
    )
    query = f"({mime_filter}) and trashed=false"

    arquivos, page_token = [], None
    while True:
        resp = service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, parents, modifiedTime)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            corpora="drive",
            driveId=drive_id,
            pageToken=page_token,
        ).execute()

        arquivos.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return arquivos


def baixar_arquivo(file_id: str, mime_type: str) -> bytes:
    service = _build_service()

    EXPORT_MAP = {
        "application/vnd.google-apps.document": "text/plain",
        "application/vnd.google-apps.spreadsheet": "text/csv",
        "application/vnd.google-apps.presentation": "text/plain",
    }

    if mime_type in EXPORT_MAP:
        resp = service.files().export_media(
            fileId=file_id, mimeType=EXPORT_MAP[mime_type]
        ).execute()
    else:
        resp = service.files().get_media(
            fileId=file_id, supportsAllDrives=True
        ).execute()

    return resp
