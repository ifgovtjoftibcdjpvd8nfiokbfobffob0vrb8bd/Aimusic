import random, os
from pyrogram import Client, filters, enums 
from ANNIEMUSIC import app
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_USERNAME

@app.on_message(filters.command(["genpassword", 'genpw']))
async def password(bot, update):
    message = await update.reply_text(text="Pʀᴏᴄᴇꜱꜱɪɴɢ..")
    characters = "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+"
    if len(update.command) > 1:
        qw = update.text.split(" ", 1)[1]
    else:
        ST = ["5", "7", "6", "9", "10", "12", "14", "8", "13"] 
        qw = random.choice(ST)
    
    try:
        limit = int(qw)
        if limit < 1:
            raise ValueError("Password length must be positive.")
    except ValueError:
        return await message.edit_text("Please enter a valid positive number for the password length.")
    
    random_value = "".join(random.choices(characters, k=limit))
    
    txt = f"<b>Lɪᴍɪᴛ:</b> {str(limit)} \n<b>Pᴀꜱꜱᴡᴏʀᴅ:</b> <code>{random_value}</code>"
    btn = InlineKeyboardMarkup([[InlineKeyboardButton('𝗔𝗗𝗗 𝗠𝗘', url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]])
    await message.edit_text(text=txt, reply_markup=btn, parse_mode=enums.ParseMode.HTML)
