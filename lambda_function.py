import requests
import re
import psycopg2
import os
from datetime import datetime
from companies import COMPANIES

def lambda_handler(event, context):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()

    new_count = 0

    for company in COMPANIES:
        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
        response = requests.get(url)
        data = response.json()

        for job in data.get("jobs", []):
            title_lower = job["title"].lower()
            if re.search(r'\bintern\b', title_lower) and "engineer" in title_lower:

                cursor.execute("SELECT id FROM postings WHERE greenhouse_id = %s", (job["id"],))
                existing = cursor.fetchone()

                if not existing:
                    cursor.execute(
                        "INSERT INTO postings (greenhouse_id, company, title, location, url, discovered_at) VALUES (%s, %s, %s, %s, %s, %s)",
                        (job["id"], company, job["title"], job["location"]["name"], job["absolute_url"], datetime.now())
                    )
                    new_count += 1

    conn.commit()
    conn.close()

    return {"statusCode": 200, "body": f"Found {new_count} new postings"}