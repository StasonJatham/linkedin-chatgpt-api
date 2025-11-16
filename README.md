# 🔍 LinkedIn Auto-Assistant

This project demonstrates how a Python service *could* theoretically automate LinkedIn using ChatGPT Web for content generation, comments without token costs — including Search and Image generation.

The research Project worked like this: 
- Parse User Feed
- Get random Post with filter list
- Like and Comment
- Add new friends
- Sleep and Continue

This resulted in a fail of ca. 250 followers and much more engagement in the course fo 30 days.

For this to work the Browser must be prepped, a fresh browser will trigger bot detectiomn. YOu have to browse the web first, then handle logins manually yourself, then youa re good to go for about 3 days.

**⚠️ Using it this way is prohibited, unsafe, and may be illegal.**  
**⚠️ This project must NOT be used with real accounts.**

This repository exists **only** for technical research.

---

## ⚠️ Critical Warning

### 🚫 High Risk of Account Bans  
This project interacts with third\-party platforms in ways that may violate their Terms of Service, including:

- Automated interaction  
- Scraping  
- Circumventing API billing  
- Browser automation that mimics human behavior  

Using this against any real service can result in:

- ❌ Permanent OpenAI account bans  
- ❌ Permanent LinkedIn account bans  
- ❌ IP blacklisting  
- ❌ Legal consequences  

> **Do NOT use this in production.**  
> **Do NOT connect it to real accounts.**  
> **Use at your own risk.**

---

## 📘 Overview

This research prototype demonstrates:

- Browser-driven automation  
- End-to-end content generation pipelines  
- LLM-assisted social posting logic  
- A small FastAPI service for experimentation  

### ⚠️ Important Note  
This is **not** an API client.  
It **does not** use the official OpenAI API.  
It **must not** be used to avoid legitimate API costs.

---

## 🛑 Ethics \& Usage Disclaimer

### You must NOT use this for:
- 🚫 Circumventing payment systems  
- 🚫 Automating real user accounts  
- 🚫 Impersonating humans  
- 🚫 Spamming, phishing, or mass posting  
- 🚫 Growth\-hacking or engagement fraud  

### You are fully responsible for your actions  
Any misuse of this project is entirely your liability.

---

## ⚙️ Installation

```bash
python \-m venv .venv  
source .venv/bin/activate  
pip install \-r requirements.txt  
```

---

## ▶️ Local Development

```bash
uvicorn main:app \-\-reload  
```

Starts the local FastAPI server with auto-reload enabled.

---
