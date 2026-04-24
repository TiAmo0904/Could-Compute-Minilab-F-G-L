from flask import Flask, request
import requests
import uuid

app = Flask(__name__)

DATA = "http://47.93.33.52:5000"
EVENT_FUNC = "https://submisson-event-ixepzwsdec.cn-beijing.fcapp.run"


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json() or {}

    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    image_url = (data.get("image_url") or "").strip()
    filename = (data.get("filename") or "").strip()

    missing = []

    if not title:
        missing.append("title")
    if not description:
        missing.append("description")
    if not image_url:
        missing.append("image_url")
    if not filename:
        missing.append("filename")

    if missing:
        status = "INCOMPLETE"
        status_detail = "Missing: " + ", ".join(missing)
    else:
        status = "PENDING"
        status_detail = "All fields submitted, awaiting processing"

    sid = str(uuid.uuid4())

    payload = {
        "id": sid,
        "title": title,
        "description": description,
        "image_url": image_url,
        "filename": filename,
        "status": status,
        "status_detail": status_detail
    }

    requests.post(f"{DATA}/submissions", json=payload, timeout=5)
    requests.post(EVENT_FUNC, json=payload, timeout=5)

    return payload


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)