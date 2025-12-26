import os
import json
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types

token = os.getenv("MY_VAR") ## Environmental variable
bot = AsyncTeleBot(token)


accounts_file = "accounts.json"
ranks = ["Junior", "Mid", "Senior", "Cisco Master","Goat", "Ago", "Jaan Penjam"]
if os.path.exists(accounts_file):
    with open(accounts_file, "r") as f:
        accounts = json.load(f)
else:
    accounts = {}

def save_accounts():
    with open(accounts_file, "w") as file:
        json.dump(accounts, file, indent=4)

def nickname_unique(name: str) -> bool:
    for uid, data in accounts.items():
        if data["username"] == name:
            return False
    return True

usernames = {}
for uid in accounts:
    usernames[accounts[uid]["username"]] = uid
user_states = {}
print(usernames)

@bot.message_handler(commands=['start']) ## Menu that pops up after /start command
async def start(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Create account", "My Info", "Check statistics", "Play") ## Buttons
    await bot.send_message(message.chat.id,"Salutasions, Fella! Choose activity:",reply_markup=kb )

@bot.message_handler(content_types=['text'])
async def handle_message(message):

    user_id = str(message.from_user.id)

    if user_id in user_states: ## Handle user states
        if user_states[user_id] == "choosing_nickname": ## User is choosing nickname
            nickname = message.text.strip()
        

            if not nickname_unique(nickname):
                await bot.send_message(message.chat.id, f"Nickname {nickname} already exists")
                return

            accounts[user_id] = {
                "username": nickname,
                "rank" : "Junior",
                "trophies": 0,
                "wins": 0,
                "losses": 0,
                "games": 0,
            }
            save_accounts()
            user_states[user_id] = None
            await bot.send_message(message.chat.id, f"Account created your nickname is: {nickname} ")

        if user_states[user_id] == "choosing_opponent":
            opponent_nickname = message.text.strip()
            if opponent_nickname not in usernames.keys():
                await bot.send_message(message.chat.id, f"There is no such player. Try again...")
            else:
                await bot.send_message(message.chat.id, f"You chose {opponent_nickname}, sending match request")


    if message.text == "Create account":
        if user_id in accounts:
            await bot.send_message(message.chat.id,"You already have an account")
        else:
            await bot.send_message(message.chat.id,"Please enter a nickname:")
            user_states[user_id] = "choosing_nickname"

    elif message.text == "Play":
        await bot.send_message(message.chat.id,"Coming soon")
        await bot.send_message(message.chat.id, "Choose Player to play against...")
        user_states[user_id] = "choosing_opponent"

    elif message.text == "Check statistics": ## Check statistics of all players, in future if list is too big, will split it by hundreds
        place = 1
        accounts_sorted_by_trophies = sorted(accounts.items(), key=lambda x: x[1]["trophies"], reverse=True)
        for account, trophies in accounts_sorted_by_trophies:
            await bot.send_message(message.chat.id, f"({place}) {accounts[account]["username"]} : {accounts[account]['trophies']}")
            place += 1


    elif message.text == "My Info":
        if user_id in accounts:
            await bot.send_message(message.chat.id, "Your info:")
            await bot.send_message(message.chat.id,
                                   "Nickname: " + str(accounts[user_id]["username"]) + "\n"
                                    "Rank: " + str(accounts[user_id]["rank"]) + "\n"
                                   "Games: " + str(accounts[user_id]["games"]) + "\n"
                                   "Wins: " + str(accounts[user_id]["wins"]) + "\n"
                                   "Losses: " + str(accounts[user_id]["losses"]) + "\n"
                                   )

        else:
            await bot.send_message(message.chat.id, "You don't have any account")
            return

if __name__ == '__main__':
    asyncio.run(bot.polling())