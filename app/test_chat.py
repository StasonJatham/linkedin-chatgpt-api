# test_chat.py
import requests

BASE = "http://localhost:8000"


def test_chat_default():
    payload = {
        "message": "Hallo, wie geht es dir?",
        "web_search": False,
        "image_gen": False,
        "deep_research": False,
    }
    resp = requests.post(f"{BASE}/chat", json=payload)
    resp.raise_for_status()
    data = resp.json()
    assert "result" in data
    assert data["mode"] == "default"
    print("Chat-Default:", data["result"])


if __name__ == "__main__":
    test_chat_default()
