import requests
import re

url = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
response = requests.get(url)
data = response.json()

for job in data["jobs"]:
    title_lower = job["title"].lower()
    if re.search(r'\bintern\b', title_lower) and "engineer" in title_lower:
        print(job["title"])