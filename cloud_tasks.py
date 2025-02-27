from google.cloud import tasks_v2
import json
import os
from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPICallError, InvalidArgument, NotFound

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(BASE_DIR)

PROJECT_ID = os.environ.get("PROJECT_ID")
CLOUD_RUN_URL = os.environ.get("CLOUD_RUN_URL")
QUEUE_NAME = os.environ.get("QUEUE_NAME")
LOCATION =os.environ.get("LOCATION")

def create_cloud_task(request_id):
    """Creates a task in Google Cloud Tasks."""
    if not PROJECT_ID or not CLOUD_RUN_URL:
        print("Error: Missing required environment variables (PROJECT_ID, CLOUD_RUN_URL)")
        return None

    try:
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(PROJECT_ID, LOCATION, QUEUE_NAME)

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": CLOUD_RUN_URL,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"request_id": request_id}).encode(),
            }
        }

        response = client.create_task(request={"parent": parent, "task": task})
        print(f"Created Cloud Task: {response.name}")
        return response.name

    except NotFound:
        print(f"Error: Task queue '{QUEUE_NAME}' not found in project '{PROJECT_ID}'.")
    except InvalidArgument as e:
        print(f"Invalid request: {e}")
    except GoogleAPICallError as e:
        print(f"API call error: {e}")
    except Exception as e:
        print(f"Unexpected error creating Cloud Task: {e}")

    return None
