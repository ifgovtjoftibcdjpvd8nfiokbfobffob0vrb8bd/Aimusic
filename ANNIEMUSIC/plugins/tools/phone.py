from pyrogram import Client, filters
import requests
from ANNIEMUSIC import app

API_KEY = "f66950368a61ebad3cba9b5924b4532d"
API_URL = "http://apilayer.net/api/validate"

def send_message(message, text):
    message.reply_text(text)

@app.on_message(filters.command("phone"))
def check_phone(client, message):
    if len(message.command) < 2:
        send_message(message, "Please provide a phone number to check. Usage: /phone <number>")
        return

    number = message.command[1]

    try:
        response = requests.get(API_URL, params={
            "access_key": API_KEY,
            "number": number,
            "country_code": "",
            "format": 1
        })
        response.raise_for_status()
        data = response.json()

        if not data.get("valid"):
            send_message(message, "The phone number is invalid.")
            return

        country_code = data.get("country_code", "N/A")
        country_name = data.get("country_name", "N/A")
        location = data.get("location", "N/A")
        carrier = data.get("carrier", "N/A")
        line_type = data.get("line_type", "N/A")
        valid = data.get("valid", False)

        response_text = (
            f"**Valid:** {valid}\n"
            f"**Phone Number:** {number}\n"
            f"**Country Code:** {country_code}\n"
            f"**Country Name:** {country_name}\n"
            f"**Location:** {location}\n"
            f"**Carrier:** {carrier}\n"
            f"**Device Type:** {line_type}"
        )

        send_message(message, response_text)
    except requests.exceptions.RequestException as e:
        send_message(message, f"Network error: {str(e)}")
    except Exception as e:
        send_message(message, f"An error occurred: {str(e)}")
