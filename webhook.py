import requests
import os
def send_alert_to_webhook(request_id, status, message):
    """Send a webhook notification to a Postman mock server."""
    webhook_url = f'{os.environ.get("WEBHOOK_URL")}/success-endpoint'
    if not webhook_url:
        print("WEBHOOK_URL not configured.")
        return
    payload = {
        "text": f"Request {request_id} has completed processing",
        "message": message,
        "status":status,
    }
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send webhook to Postman mock server: {response.text}")
        else:
            print("Webhook sent successfully to Postman mock server.")
    except Exception as e:
        print(f"Error sending webhook: {e}")