import os
import json
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types

token = os.getenv("MY_VAR") ## Environmental variable
bot = AsyncTeleBot(token)

@bot.message_handler(commands=['start'])
async def start(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Create account", "Play") ## Buttons
    await bot.send_message(message.chat.id,"Salutasions, Fella! Choose activity:",reply_markup=kb )


if __name__ == '__main__':
    asyncio.run(bot.polling())