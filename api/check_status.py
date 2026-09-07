import requests
from requests.auth import HTTPBasicAuth

URL = "http://172.16.17.100:8002/api/ApiStatusCheck"

USERNAME = "wssp_api_user"
PASSWORD = "StrongPassword@123"
API_KEY = "X-123ABC456"

headers = {
    "x-api-key": API_KEY
}

response = requests.get(
    URL,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    headers=headers,
    timeout=10
)

print("Status Code:", response.status_code)
print("Response Text:", response.text)
