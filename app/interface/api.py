from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.orquestracao.orquestrador import perguntar

app = FastAPI(title="Germano G2")


def _chat_response(text: str) -> JSONResponse:
    return JSONResponse(content={
        "cardsV2": [{
            "cardId": "reply",
            "card": {
                "sections": [{
                    "widgets": [{
                        "textParagraph": {"text": text}
                    }]
                }]
            }
        }]
    })


@app.post("/chat")
async def webhook_google_chat(request: Request):
    body = await request.json()
    event_type = body.get("type", "")

    if event_type == "ADDED_TO_SPACE":
        return _chat_response("Olá! Sou o Germano 🤖 Pergunte qualquer coisa sobre os documentos.")

    if event_type == "REMOVED_FROM_SPACE":
        return JSONResponse(content={})

    mensagem = body.get("message", {}).get("text", "").strip()
    if not mensagem:
        return _chat_response("Não entendi sua mensagem. Tente novamente.")

    resposta = perguntar(mensagem)
    return _chat_response(resposta)


@app.get("/health")
async def health():
    return {"status": "ok"}
