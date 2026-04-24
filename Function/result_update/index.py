import json
import requests

# Base API endpoint
DATA = "http://47.93.33.52:5000" 

def handler(event, context):

    # Decode bytes input if needed
    if isinstance(event, (bytes, bytearray)):
        event = event.decode()

    # Parse JSON string into dict
    if isinstance(event, str):
        event = json.loads(event)

    # Extract request body
    body = event.get("body", "{}")

    # Parse body if it is a string
    if isinstance(body, str):
        data = json.loads(body)
    else:
        data = body

    # Get required fields
    submission_id = data.get("id")
    status = data.get("status")
    status_detail = data.get("status_detail", "")
    
    # Debug logs
    print("PARSED DATA:", data)
    print("ID:", submission_id)
    print("STATUS:", status)

    # Validate input
    if not submission_id or not status:
        return {"error": "invalid payload"}

    # Send update request to backend service
    requests.put(
    DATA + "/submissions/" + submission_id,
    json={
        "status": status,
        "status_detail": status_detail
    },
    timeout=5
)

    # Return success response
    return {"message": "updated"}