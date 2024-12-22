from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from ANNIEMUSIC import app

@app.on_message(filters.command("population"))
def country_command_handler(client: Client, message: Message):
    if len(message.text.split()) < 2:
        return message.reply_text("Please provide a valid country code. Example: /population US")

    country_code = message.text.split(maxsplit=1)[1].strip()

    api_url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()

        country_info = response.json()
        if country_info:
            country_name = country_info[0].get("name", {}).get("common", "N/A")
            capital = country_info[0].get("capital", ["N/A"])[0]
            population = country_info[0].get("population", "N/A")

            response_text = (
                f"Country Information\n\n"
                f"Name: {country_name}\n"
                f"Capital: {capital}\n"
                f"Population: {population}"
            )
        else:
            response_text = "Error fetching country information from the API."
    except requests.exceptions.HTTPError:
        response_text = "Please enter a correct country code."
    except Exception as err:
        response_text = "An error occurred. Please contact support."

    message.reply_text(response_text)
