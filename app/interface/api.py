from fastapi import FastAPI, Request
from app.orquestracao.orquestrador import perguntar

app = FastAPI(title="Germano G2")


@app.post("/chat")
async def webhook_google_chat(request: Request):
    body = await request.json()

    # Google Chat envia o tipo do evento
    event_type = body.get("type", "")

    # ADDED_TO_SPACE ou REMOVED_FROM_SPACE — apenas saudação
    if event_type == "ADDED_TO_SPACE":
        return {"text": "Olá! Sou o Germano 🤖 Pergunte qualquer coisa sobre os documentos."}

    if event_type == "REMOVED_FROM_SPACE":
        return {}

    # MESSAGE — pergunta real do usuário
    mensagem = body.get("message", {}).get("text", "").strip()
    if not mensagem:
        return {"text": "Não entendi sua mensagem. Tente novamente."}

    resposta = perguntar(mensagem)
    return {"text": resposta}


@app.get("/health")
async def health():
    return {"status": "ok"}
