# ChatGPT Evil API

Eine schlanke API-Anwendung, die lokal über FastAPI und Uvicorn läuft – mit separaten Tests für Live-Chats und Jobs. Perfekt für interne Automatisierung, Bots oder andere abseitige Zwecke 😈

## 🚀 Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ▶️ Starten

```bash
uvicorn main:app –reload
```


## 🧪 Tests

### 💬 Live Chat

```bash
python test_chat.py
```

### ⚙️ Jobs

```bash
python test_jobs.py
```

## 📁 Struktur
- main.py – API-Einstiegspunkt
- test_chat.py – testet den Chatflow
- test_jobs.py – testet Job-Handling oder Background-Tasks
- requirements.txt – Python-Abhängigkeiten
- .venv/ – deine virtuelle Umgebung (nicht tracken!)