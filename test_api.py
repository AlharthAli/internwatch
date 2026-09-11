import requests

url = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
response = requests.get(url)
data = response.json()

print(data["jobs"][0]["title"])