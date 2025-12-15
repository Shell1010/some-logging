import bs4 
import re
import json
import requests
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

url = "https://account.aq.com/Event/Frostval"
history = "./data/acs_history.json"
other_history = "./data/counts_history.json"
output = "./data/acs_history.png"
other_output = "./data/counts_history.png"
webhook_url = "https://canary.discord.com/api/webhooks/1372012402534518874/xN9Gl0NkjPpG_eykWWaEkM7zNvIEFOZ4_Hl2sWD-UCf2Ycsm5qdDG08qq5OzjD0rvViT"
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
        "username": f"[{username}](https://account.aq.com/CharPage?id={username.replace(' ', '+')})",
        "AC_count": ac_text
    })
    position += 1



with open("./data/frostval.json", "a+") as f:
    f.truncate(0)
    json.dump(users, f, indent=4)


text = soup.get_text(" ", strip=True)

total_acs = re.search(r"Total ACs Gifted this Season:\s*([\d,]+)", text)
total_chars = re.search(r"Number of chars Received a Gift:\s*([\d,]+)", text)

data = {
    "total_acs": total_acs.group(1) if total_acs else "0",
    "total_chars": total_chars.group(1) if total_chars else "0"
}

with open("./data/frostval_totals.json", "a+") as f:
    f.truncate(0)
    json.dump(data, f, indent=4)

def update_char_totals(total_chars: int, total_acs: int):
	if os.path.exists(path=other_history):
		with open(history, "r") as f:
			data = json.load(f)
	else:
		data = []
	
	last_char_count = data[-1].get("total_chars", 0)
	current = total_chars - last_char_count
	data.append({
		"timestamp": datetime.utcnow().isoformat(),
		"total_chars": total_chars,
		"total_acs": total_acs,
		"current_chars": current
	})
	with open(history, "w") as f:
		json.dump(data, f, indent=2)
		
		
	# Chars Gifted Over Time
	dates = [datetime.fromisoformat(entry["timestamp"]) for entry in data]
	totals = [entry["current_chars"] for entry in data]
	
	plt.plot(
        dates,
        totals,
        marker="o",
        linewidth=2.5
    )

	plt.xlabel("Time (UTC)", fontsize=12)
	plt.ylabel("Chars Gifted Over Time", fontsize=12)
	plt.title("Frostval Total Chars Gifted Over Time", fontsize=16, weight="bold")
	
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
	plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
	
	plt.xticks(rotation=40, ha="right")
	plt.grid(alpha=0.25)
	plt.tight_layout(pad=2)
	
	
	plt.savefig(other_output, dpi=150, bbox_inches="tight")
	plt.close()
	

	
    
    
	
	
        

def update_and_plot_totals(total_acs_gifted: int):
    # Load or create history file
    if os.path.exists(history):
        with open(history, "r") as f:
            data = json.load(f)
    else:
        data = []

    # Append new data point
    data.append({
        "timestamp": datetime.utcnow().isoformat(),
        "total_acs": total_acs_gifted
    })

    # Save updated history
    with open(history, "w") as f:
        json.dump(data, f, indent=2)

    # Prepare data for plotting
    dates = [datetime.fromisoformat(entry["timestamp"]) for entry in data]
    totals = [entry["total_acs"] for entry in data]

    # Styling
    plt.style.use("default")  # no dark mode because GitHub renders white best
    plt.figure(figsize=(12, 6))

    plt.plot(
        dates,
        totals,
        marker="o",
        linewidth=2.5
    )

    plt.xlabel("Time (UTC)", fontsize=12)
    plt.ylabel("Total ACs Gifted", fontsize=12)
    plt.title("Frostval Total ACs Gifted Over Time", fontsize=16, weight="bold")

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.xticks(rotation=40, ha="right")
    plt.grid(alpha=0.25)
    plt.tight_layout(pad=2)

    
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()
    
    # ---- Calculate ACs gifted per hour ----
    if len(data) < 2:
        return  # not enough data yet

    rate_dates = []
    acs_per_hour = []

    for i in range(1, len(data)):
        t1 = dates[i - 1]
        t2 = dates[i]
        ac1 = totals[i - 1]
        ac2 = totals[i]

        delta_hours = (t2 - t1).total_seconds() / 3600
        if delta_hours <= 0:
            continue

        rate = (ac2 - ac1) / delta_hours

        rate_dates.append(t2)
        acs_per_hour.append(rate)

    # ---- Plot 2: ACs per hour ----
    plt.figure(figsize=(12, 6))

    plt.plot(rate_dates, acs_per_hour, marker="o", linewidth=2.5)

    plt.xlabel("Time (UTC)")
    plt.ylabel("ACs Gifted per Hour")
    plt.title("Frostval AC Distribution Rate", weight="bold")

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=40, ha="right")
    plt.grid(alpha=0.25)
    plt.tight_layout()

    plt.savefig("./data/acs_per_hour.png", dpi=150, bbox_inches="tight")
    plt.close()


update_and_plot_totals(int(data['total_acs'].replace(",", "")))
update_char_totals(int(data['total_chars'].replace(",", "")), int(data['total_acs'].replace(",", "")))

def send_plot_to_webhook(webhook_url: str, output_file: str):
    with open(output_file, "rb") as f:
        files = {
            "file": (output_file, f, "image/png")
        }

        data = {
            "content": "Updated Frostval ACs over time"
        }

        response = requests.post(webhook_url, data=data, files=files)
        response.raise_for_status()  # throw if it fails


def edit_webhook_message(webhook_url: str, message_id: str, output_file: str):
    url = f"{webhook_url}/messages/{message_id}"

    with open(output_file, "rb") as f:
        files = {
            "files[0]": (output_file, f, "image/png")
        }

        payload = {
            "content": None,
            "embeds": [
                {
                    "title": "Frostval ACs Gifted Over Time",
                    "image": {
                        "url": f"attachment://{output_file}"
                    }
                }
            ],


            "attachments": [
                {
                    "id": 0,
                    "filename": output_file
                }
            ]
        }

        response = requests.patch(
            url,
            data={"payload_json": json.dumps(payload)},
            files=files
        )

        print(response.text)
        response.raise_for_status()


edit_webhook_message(webhook_url, "1447016648140652665", output)


send_plot_to_webhook(webhook_url, other_output)
send_plot_to_webhook(webhook_url, "./data/acs_per_hour.png")