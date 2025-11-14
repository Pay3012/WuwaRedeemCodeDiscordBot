import discord
import asyncio
import requests
from bs4 import BeautifulSoup
import csv
import os

TOKEN = ""
CHANNEL_ID = 
FANDOM_URL = "https://wutheringwaves.fandom.com/wiki/Redemption_Code"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

CSV_FILE = "codes.csv"
previous_codes = set()


# ---------------------- CSV FUNCTIONS ----------------------

def load_codes_from_csv():
    """Load previously saved codes from CSV into a set."""
    if not os.path.exists(CSV_FILE):
        return set()

    codes = set()
    with open(CSV_FILE, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                codes.add(row[0])
    return codes


def save_code_to_csv(code):
    """Append a new code to the CSV file."""
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([code])


# ---------------------- SCRAPER ----------------------

async def fetch_codes():
    response = requests.get(FANDOM_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    codes = set()

    for table in soup.find_all("table", {"class": "wikitable"}):
        for row in table.find_all("tr")[1:]:
            cell = row.find("td")
            if cell:
                tag = cell.find("code")
                if tag:
                    codes.add(tag.get_text(strip=True))
    return codes


# ---------------------- MONITORING ----------------------

async def monitor_codes():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    global previous_codes

    # Load saved codes first
    previous_codes = load_codes_from_csv()
    print("Loaded codes from CSV:", previous_codes)

    # Scrape site codes
    site_codes = await fetch_codes()
    print("Fetched site codes:", site_codes)

    # Send all site codes that are NOT already saved
    startup_new_codes = site_codes - previous_codes
    for code in startup_new_codes:
        await channel.send(f"🚨 New Wuthering Waves code dropped: **{code}**")
        save_code_to_csv(code)
        previous_codes.add(code)

    # Begin monitoring loop
    while True:
        await asyncio.sleep(900)
        try:
            current_codes = await fetch_codes()
            new_codes = current_codes - previous_codes

            for code in new_codes:
                await channel.send(f"🚨 New Wuthering Waves code dropped: **{code}**")
                save_code_to_csv(code)
                previous_codes.add(code)

        except Exception as e:
            print(f"Error checking codes: {e}")


# ---------------------- DISCORD EVENTS ----------------------

@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

@client.event
async def setup_hook():
    client.loop.create_task(monitor_codes())


client.run(TOKEN)
