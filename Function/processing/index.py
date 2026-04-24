import json
import requests

UPDATE_FUNC = "https://result-update-erlglaxzph.cn-beijing.fcapp.run"

ALLOWED = (".jpg", ".jpeg", ".png")


def handler(event, context):

    print("Raw Event")
    print(event)

    # decode
    if isinstance(event, (bytes, bytearray)):
        event = event.decode()

    outer = json.loads(event)

    print("Outer")
    print(outer)

    # get body
    body = outer.get("body", "{}")

    # loads body
    data = json.loads(body)

    print("Final Data")
    print(data)

    # mian function, get target information
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    image_url = data.get("image_url", "").strip()

    # status detail logic
    missing = []

    if not title:
        missing.append("title")
    if not description:
        missing.append("description")
    if not image_url:
        missing.append("image_url")

    if not title or not description or not image_url:
        status = "INCOMPLETE"
        status_detail = "Missing: " + ", ".join(missing)

    elif len(description) < 30:
        status = "NEEDS REVISION"
        status_detail = "Description too short (min 30 characters)"

    elif not image_url.lower().endswith(ALLOWED):
        status = "NEEDS REVISION"
        status_detail = "Image format invalid (must be jpg/jpeg/png)"

    else:
        status = "READY"
        status_detail = "All checks passed successfully"

    print("STATUS:", status)

    # Update dataset
    requests.post(UPDATE_FUNC, json={
        "id": data.get("id"),
        "status": status,
        "status_detail": status_detail
    }, timeout=5)

    return {"status": status}