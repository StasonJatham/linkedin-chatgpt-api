# test_jobs.py
import time
import requests

BASE = "http://localhost:8000"


def submit_job(message: str, image_gen: bool = False):
    payload = {
        "message": message,
        "web_search": False,
        "image_gen": image_gen,
        "deep_research": False,
    }
    resp = requests.post(f"{BASE}/jobs", json=payload)
    resp.raise_for_status()
    info = resp.json()
    job_id, status = info["job_id"], info["status"]
    print(f"Job {job_id} eingereicht, Status: {status}")
    return job_id


def poll_job(job_id: int, interval: float = 1.0, timeout: float = 60.0):
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{BASE}/jobs/{job_id}")
        resp.raise_for_status()
        info = resp.json()
        print(f"Polling Job {job_id}: {info['status']}")
        if info["status"] in ("done", "failed"):
            return info
        time.sleep(interval)
    raise TimeoutError(f"Job {job_id} nach {timeout}s nicht fertig.")


if __name__ == "__main__":
    # 1) Text-Job
    # jid = submit_job("Erkläre Quantenphysik in zwei Sätzen")
    # result = poll_job(jid)
    # print("Ergebnis Text-Job:", result["result"])

    # 2) Bild-Job
    # if image to be generated
    jid2 = submit_job(
        "Bild erstellen: Erstelle ein Bild von einem Sonnenuntergang mit einem Huhn. Comic stil.",
        image_gen=True,
    )
    result2 = poll_job(jid2)
    print("Ergebnis Bild-Job:", result2["result"])
