import gspread
from oauth2client.service_account import ServiceAccountCredentials
import schedule, time, requests
from scraper import get_jobs
from config import TELEGRAM_TOKEN, CHAT_ID

def score(job):
    score = 0
    text = (job["title"] + job["skills"]).lower()

    # Core skills (your resume)
    if "sql" in text: score += 30
    if "python" in text: score += 25
    if "power bi" in text: score += 20
    if "excel" in text: score += 15

    # Role matching
    if "data analyst" in text: score += 20
    if "mis" in text: score += 15

    # Bonus
    if "dashboard" in text or "reporting" in text:
        score += 10

    return min(score, 100)

def filter_jobs(jobs):
    result = []

    for j in jobs:
        title = j["title"].lower()

        if not any(x in title for x in ["data analyst","mis","sql","python"]):
            continue

        j["score"] = score(j)
        result.append(j)

    return sorted(result, key=lambda x: x["score"], reverse=True)[:10]

def send_telegram(jobs):
    msg = ""

    for i, j in enumerate(jobs, 1):
        msg += f"""#{i} | {j['company']} | {j['title']} | {j['location']}
Match Score: {j['score']}%
Why it fits: SQL + Python + Data skills
Apply: {j['link']}

"""

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def job_task():
    jobs = get_jobs()
    top = filter_jobs(jobs)

    save_to_sheet(top)     # ✅ ADD THIS
    send_telegram(top)


def save_to_sheet(jobs):
    scope = ["https://spreadsheets.google.com/feeds"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("Daily Job Tracker").sheet1

    for j in jobs:
        sheet.append_row([
            j["company"],
            j["title"],
            j["location"],
            j["score"],
            j["link"]
        ])



# run daily
schedule.every().day.at("09:00").do(job_task)

print("Bot running...")

while True:
    schedule.run_pending()
    time.sleep(60)

