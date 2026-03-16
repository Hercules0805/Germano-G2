from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
from app.config import get_credentials, PROJECT_ID, LLM_MODEL, VERTEX_LOCATION

_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

_SYSTEM_PROMPT = (
    "Você é o Germano, um assistente inteligente que responde perguntas "
    "com base exclusivamente nos documentos fornecidos como contexto. "
    "Se a resposta não estiver no contexto, diga que não encontrou informação suficiente. "
    "Responda de forma clara e objetiva em português."
)


def _init():
    aiplatform.init(
        project=PROJECT_ID, location=VERTEX_LOCATION,
        credentials=get_credentials(_SCOPES),
    )


def gerar_resposta(pergunta: str, contextos: list[str]) -> str:
    _init()
    model = GenerativeModel(LLM_MODEL, system_instruction=_SYSTEM_PROMPT)

    contexto_formatado = "\n\n---\n\n".join(contextos)
    prompt = (
        f"Contexto:\n{contexto_formatado}\n\n"
        f"Pergunta: {pergunta}\n\n"
        f"Resposta:"
    )

    response = model.generate_content(prompt)
    return response.text
