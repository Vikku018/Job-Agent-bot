import requests
from bs4 import BeautifulSoup

def get_jobs():
    jobs = []

    url = "https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=India&f_TPR=r86400"

    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")

    cards = soup.find_all("div", class_="base-card")

    for c in cards[:25]:
        try:
            title = c.find("h3").text.strip()
            company = c.find("h4").text.strip()
            location = c.find("span", class_="job-search-card__location").text.strip()
            link = c.find("a")["href"]

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "skills": "",
                "link": link
            })
        except:
            continue

    return jobs