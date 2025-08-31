import discord
import asyncio
import requests
from bs4 import BeautifulSoup

TOKEN = ""
CHANNEL_ID =   
FANDOM_URL = "https://wutheringwaves.fandom.com/wiki/Redemption_Code"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

previous_codes = set()

async def fetch_codes():
    response = requests.get(FANDOM_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    codes = set()

    # Find all tables with class 'wikitable'
    for table in soup.find_all("table", {"class": "wikitable"}):
        for row in table.find_all("tr")[1:]:  # skip header
            cell = row.find("td")
            if cell:
                code_tag = cell.find("code")
                if code_tag:
                    codes.add(code_tag.get_text(strip=True))
    return codes

async def monitor_codes():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    global previous_codes

    previous_codes = await fetch_codes()
    if previous_codes:
        await channel.send("📜 Current Wuthering Waves codes:\n" + 
                           "\n".join(f"🔑 **{code}**" for code in previous_codes))

    while True:
        await asyncio.sleep(900)
        try:
            current_codes = await fetch_codes()
            new = current_codes - previous_codes
            if new:
                for code in new:
                    await channel.send(f"🚨 New Wuthering Waves code dropped: **{code}**")
                previous_codes = current_codes
        except Exception as e:
            print(f"Error checking codes: {e}")

@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

@client.event
async def setup_hook():
    client.loop.create_task(monitor_codes())

client.run(TOKEN)