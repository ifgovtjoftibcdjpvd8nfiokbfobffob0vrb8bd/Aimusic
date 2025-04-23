from typing import Union
import re
import random
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from ANNIEMUSIC import app
from ANNIEMUSIC.utils.inline.help import (
    first_page,
    second_page,
    help_back_markup,
    private_help_panel
)
from ANNIEMUSIC.utils.inline.start import private_panel
from ANNIEMUSIC.utils.database import get_lang
from ANNIEMUSIC.utils.decorators.language import LanguageStart, languageCB
from config import BANNED_USERS, SUPPORT_CHAT
from strings import get_string, helpers

@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("open_help") & ~BANNED_USERS)
@LanguageStart
async def helper_private(client: app, update: Union[Message, types.CallbackQuery], _):
    is_callback = isinstance(update, types.CallbackQuery)
    language = await get_lang(update.from_user.id)
    _ = get_string(language)
    keyboard = first_page(_)
    text = _["help_1"].format(SUPPORT_CHAT)
    if is_callback:
        message = update.message
        await update.answer()
        await message.edit_text(
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    else:
        message = update
        await message.delete()
        await message.reply_text(
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )


@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(
        _["help_2"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )


@app.on_callback_query(filters.regex(r"help_callback hb(\d+)_p(\d+)") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    cb_match = re.match(r"help_callback hb(\d+)_p(\d+)", CallbackQuery.data)
    if cb_match:
        number = int(cb_match.group(1))
        current_page = int(cb_match.group(2))
        help_text = getattr(helpers, f'HELP_{number}', None)
        if help_text:
            keyboard = help_back_markup(_, current_page)
            await CallbackQuery.edit_message_text(
                help_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        else:
            await CallbackQuery.answer("Invalid help topic.", show_alert=True)
    else:
        await CallbackQuery.answer("Invalid callback.", show_alert=True)


@app.on_callback_query(filters.regex(r"help_next_(\d+)") & ~BANNED_USERS)
@languageCB
async def help_next_cb(client, CallbackQuery, _):
    match = re.match(r"help_next_(\d+)", CallbackQuery.data)
    if match:
        next_page = int(match.group(1))
        if next_page == 2:
            keyboard = second_page(_)
            text = _["help_1"].format(SUPPORT_CHAT)
            await CallbackQuery.edit_message_text(
                text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        else:
            await CallbackQuery.answer("No more pages.", show_alert=True)
    else:
        await CallbackQuery.answer("Invalid callback data.", show_alert=True)


@app.on_callback_query(filters.regex(r"help_prev_(\d+)") & ~BANNED_USERS)
@languageCB
async def help_prev_cb(client, CallbackQuery, _):
    match = re.match(r"help_prev_(\d+)", CallbackQuery.data)
    if match:
        prev_page = int(match.group(1))
        if prev_page == 1:
            keyboard = first_page(_)
            text = _["help_1"].format(SUPPORT_CHAT)
            await CallbackQuery.edit_message_text(
                text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        else:
            await CallbackQuery.answer("No previous page.", show_alert=True)
    else:
        await CallbackQuery.answer("Invalid callback data.", show_alert=True)


@app.on_callback_query(filters.regex(r"help_back_(\d+)") & ~BANNED_USERS)
@languageCB
async def help_back_cb(client, CallbackQuery, _):
    match = re.match(r"help_back_(\d+)", CallbackQuery.data)
    if match:
        current_page = int(match.group(1))
        if current_page == 1:
            keyboard = first_page(_)
        elif current_page == 2:
            keyboard = second_page(_)
        else:
            await CallbackQuery.answer("Invalid page.", show_alert=True)
            return
        text = _["help_1"].format(SUPPORT_CHAT)
        await CallbackQuery.edit_message_text(
            text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    else:
        await CallbackQuery.answer("Invalid callback data.", show_alert=True)

@app.on_callback_query(filters.regex("back_to_main") & ~BANNED_USERS)
@languageCB
async def back_to_main_cb(client, CallbackQuery, _):
    out = private_panel(_)
    await CallbackQuery.edit_message_text(
        text=_["start_2"].format(CallbackQuery.from_user.mention, app.mention),
        reply_markup=InlineKeyboardMarkup(out),
        disable_web_page_preview=True
    )