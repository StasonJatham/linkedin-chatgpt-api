from multiprocessing import Queue
from dataclasses import dataclass

# Gemeinsame Datenstruktur
@dataclass
class ChatRequest:
    id: str
    message: str

@dataclass
class ChatResponse:
    id: str
    result: str

# Gemeinsame Queues
input_queue = Queue()
output_queue = Queue()
