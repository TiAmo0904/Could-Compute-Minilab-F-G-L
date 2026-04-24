import json
import requests

PROCESS_FUNC = "https://processing-rqosazejkv.cn-beijing.fcapp.run"

# Is this method called the Event Gateway?
def handler(event, context):

    # Ensure that the data are transformed into python strings
    # and could be ready for later on JSON operation.
    if isinstance(event, (bytes, bytearray)):
        event = event.decode()

    # Information about the HTTP Request
    outer = json.loads(event)

    # Only the effective payload is extracted.
    body = outer.get("body", "{}")

    # transform the body message.
    data = json.loads(body)

    print("FORWARD CLEAN DATA:", data)

    # Send the body data to backend processing function using POST method.
    requests.post(PROCESS_FUNC, json=data, timeout=5)
    # The backend processing function always receives data of the same JSON format.

    return {"message": "clean event forwarded"}
