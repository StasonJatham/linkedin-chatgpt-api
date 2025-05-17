from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uuid
import threading
import time

from shared import input_queue, output_queue, ChatRequest, ChatResponse

app = FastAPI()

# Einfaches Speicherobjekt für Antworten
pending_responses = {}

# Request-Body
class MessageIn(BaseModel):
    message: str

# Response-Body
class MessageOut(BaseModel):
    id: str
    result: str

@app.post("/chat", response_model=MessageOut)
def send_chat_message(data: MessageIn, bg: BackgroundTasks):
    request_id = str(uuid.uuid4())
    input_queue.put(ChatRequest(id=request_id, message=data.message))
    bg.add_task(wait_for_result, request_id)
    return {"id": request_id, "result": "pending"}

@app.get("/chat/{request_id}", response_model=MessageOut)
def get_chat_result(request_id: str):
    if request_id not in pending_responses:
        return {"id": request_id, "result": "pending"}
    return {"id": request_id, "result": pending_responses.pop(request_id)}

def wait_for_result(request_id: str):
    # Warte auf Ergebnis vom Worker
    while True:
        res: ChatResponse = output_queue.get()
        if res.id == request_id:
            pending_responses[res.id] = res.result
            break
        else:
            # Wieder in die Queue legen, wenn es nicht der richtige ist
            output_queue.put(res)
            time.sleep(0.05)

# Optional: server automatisch starten
if __name__ == "__main__":
    threading.Thread(target=start_worker, daemon=True).start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
