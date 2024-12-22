from pyrogram import Client, filters
import requests
from ANNIEMUSIC import app

def get_pypi_info(package_name):
    try:
        api_url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(api_url)
        return response.json()
    except Exception as e:
        print(f"Error fetching PyPI information: {e}")
        return None

@app.on_message(filters.command("pypi"))
async def pypi_info_command(client, message):
    if len(message.command) < 2:
        await message.reply("Please provide a package name after the /pypi command.")
        return
    package_name = message.command[1]
    pypi_info = get_pypi_info(package_name)
    if pypi_info:
        info_message = (
            f"**Package Name:** {pypi_info['info']['name']}\n"
            f"**Latest Version:** {pypi_info['info']['version']}\n"
            f"**Description:** {pypi_info['info']['summary']}\n"
            f"**Project URL:** {pypi_info['info']['project_urls'].get('Homepage', 'N/A')}"
        )
        await message.reply(info_message)
    else:
        await message.reply("Failed to fetch information from PyPI.")