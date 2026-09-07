import requests
from requests.auth import HTTPBasicAuth
import json

URL = "http://172.16.17.100:8002/api/dshbMonthWiseData"

USERNAME = "wssp_api_user"
PASSWORD = "StrongPassword@123"
API_KEY = "X-123ABC456"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "departmentId": 1001,
    "serviceId": None,
    "startdate": "2026-02-01",
    "enddate": "2026-02-28"
}

response = requests.post(
    URL,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    headers=headers,
    json=payload,
    timeout=10
)

print("Status Code:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=4))
