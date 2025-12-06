import bs4 
import re
import json
import requests


url = "https://account.aq.com/Event/Frostval"
headers = {
    "cookie": "__cflb=0H28vnxFdh6KtiojTf63QjxSL2uBCoLzh55W7zazvEH",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0"

}

html = requests.get(url, headers=headers).text

soup = bs4.BeautifulSoup(html, "html.parser")

users = []
table_rows = soup.select("table tbody tr")
position = 1
for row in table_rows:
    cols = row.find_all("td")
    if len(cols) < 2:
        continue
    username = cols[0].get_text(strip=True)

    a_tag = cols[0].find("a")
    if a_tag and a_tag.next_sibling:
        username = a_tag.next_sibling.strip()

    ac_text = cols[1].get_text(strip=True)

    users.append({
        "position": position,
        "username": username,
        "AC_count": ac_text
    })
    position += 1



with open("./data/frostval.json", "w") as f:
    f.truncate(0)
    json.dump(users, f, indent=4)


text = soup.get_text(" ", strip=True)

total_acs = re.search(r"Total ACs Gifted this Season:\s*([\d,]+)", text)
total_chars = re.search(r"Number of chars Received a Gift:\s*([\d,]+)", text)

with open("./data/frostval_totals.json", "w") as f:
    f.truncate(0)
    json.dump({
        "total_acs": total_acs,
        "total_chars": total_chars
    }, f, indent=4)

