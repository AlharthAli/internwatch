from openpyxl import Workbook
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

cursor.execute("SELECT company, title, location, url, discovered_at FROM postings")
rows = cursor.fetchall()

wb = Workbook()
ws = wb.active
ws.append(["Company", "Title", "Location", "URL", "Discovered At"])

for row in rows:
    ws.append(row)

wb.save("internships.xlsx")
conn.close()