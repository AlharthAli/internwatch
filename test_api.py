import requests
import re
from companies import COMPANIES

for company in COMPANIES:
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
    response = requests.get(url)
    data = response.json()
    
    for job in data.get("jobs", []):
        title_lower = job["title"].lower()
        if re.search(r'\bintern\b', title_lower) and "engineer" in title_lower:
            print(f"[{company}] {job['title']}")