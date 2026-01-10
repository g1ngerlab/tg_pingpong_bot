import os
import json
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import random
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TOKEN") ## Environmental variable
bot = AsyncTeleBot(token)

current_matches = {} ## format - {opponent id : self id}
active_games = {}

accounts_file = "accounts.json"
ranks = ["Junior", "Mid", "Senior", "Cisco Master","Goat", "Ago", "Jaan Penjam"] ##Ranks
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
            usernames[nickname] = user_id ## update usernames with new user
            save_accounts()
            user_states[user_id] = None
            await bot.send_message(message.chat.id, f"Account created your nickname is: {nickname} ")

        if user_states[user_id] == "choosing_opponent":
            opponent_nickname = message.text.strip()
            if opponent_nickname not in usernames.keys():
                await bot.send_message(message.chat.id, f"There is no such player. Try again...")
                user_states[user_id] = None
                return
            opponent_user_id = usernames[opponent_nickname]
            if opponent_user_id == user_id:
                await bot.send_message(message.chat.id, f"You chose yourself, how smart haHAha...")
                user_states[user_id] = None
                return
            else:
                current_matches[opponent_user_id] = user_id
                kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
                kb.add("Accept match", "Decline match")

                await bot.send_message(
                    opponent_user_id,
                    f"🏓 You have been invited to a match by {accounts[user_id]['username']}",
                    reply_markup=kb
                )
                await bot.send_message(message.chat.id,"Request sent")
                user_states[user_id] = None


    if message.text == "Create account":
        if user_id in accounts:
            await bot.send_message(message.chat.id,"You already have an account")
        else:
            await bot.send_message(message.chat.id,"Please enter a nickname:")
            user_states[user_id] = "choosing_nickname"

    elif message.text == "Play":
        await bot.send_message(message.chat.id, "Choose Player to play against...")
        user_states[user_id] = "choosing_opponent"

    elif message.text == "Check statistics": ## Check statistics of all players, in future if list is too big, will split it by hundreds
        place = 1
        accounts_sorted_by_trophies = sorted(accounts.items(), key=lambda x: x[1]["trophies"], reverse=True)
        for account, trophies in accounts_sorted_by_trophies:
            await bot.send_message(message.chat.id, f"({place}) {accounts[account]["username"]} : {accounts[account]['trophies']}")
            place += 1

    elif message.text == "Accept match":
        if user_id not in current_matches:
            await bot.send_message(message.chat.id, f"There is no match")
            return
        else:
            challenger_id = current_matches.pop(user_id)
            await bot.send_message(
                message.chat.id,
                f"✅ Match accepted! Playing against {accounts[challenger_id]['username']}"
            )

            await bot.send_message(
                challenger_id,
                f"🎉 {accounts[user_id]['username']} accepted your match request!"
            )
            active_games[user_id] = {"opponent": challenger_id, "result": None}
            active_games[challenger_id] = {"opponent": user_id, "result": None}

            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add("I won", "I lost")

            await bot.send_message(user_id, "Match started!", reply_markup=kb)
            await bot.send_message(challenger_id, "Match started!", reply_markup=kb)

            user_states[user_id] = "choosing_winner"
            user_states[challenger_id] = "choosing_winner"

    if message.text == "I won" or message.text == "I lost" and user_states[user_id] == "choosing_winner":
        if message.text == "I won":
            result = "won"
        else:
            result = "lost"
        active_games[user_id]["result"] = result
        opponent_id = active_games[user_id]["opponent"]

        await bot.send_message(message.chat.id,"Result submitted, waiting for the opponent")
        if active_games[opponent_id]["result"] is None:
            return

        my_result = active_games[user_id]["result"]
        opps_result = active_games[opponent_id]["result"]

        if opps_result != my_result:
            winner = user_id if my_result == "win" else opponent_id
            loser = opponent_id if winner == user_id else user_id

            trophies_won = random.randint(28, 33)
            trophies_lost = random.randint(28, 33)

            accounts[winner]["wins"] += 1
            accounts[loser]["losses"] += 1
            accounts[winner]["games"] += 1
            accounts[loser]["games"] += 1
            accounts[winner]["trophies"] += trophies_won
            if accounts[loser]["trophies"] > 34:
                accounts[loser]["trophies"] -= trophies_lost
            else:
                trophies_lost = 0
            if accounts[winner]["trophies"] > 150 and accounts[winner]["trophies"] < 300 :
                accounts[winner]["rank"] = ranks[1]
            elif accounts[winner]["trophies"] > 299 and accounts[winner]["trophies"] < 449 :
                accounts[winner]["rank"] = ranks[2]
            elif accounts[winner]["trophies"] > 449 and accounts[winner]["trophies"] < 599 :
                accounts[winner]["rank"] = ranks[3]
            elif accounts[winner]["trophies"] > 749 and accounts[winner]["trophies"] < 899 :
                accounts[winner]["rank"] = ranks[4]
            elif accounts[winner]["trophies"] > 899 and accounts[winner]["trophies"] < 1049 :
                accounts[winner]["rank"] = ranks[5]
            elif accounts[winner]["trophies"] > 1049 and accounts[winner]["trophies"] < 1199 :
                accounts[winner]["rank"] = ranks[6]

            elif accounts[loser]["trophies"] > 150 and accounts[loser]["trophies"] < 300 :
                accounts[loser]["rank"] = ranks[1]
            elif accounts[loser]["trophies"] > 299 and accounts[loser]["trophies"] < 449 :
                accounts[loser]["rank"] = ranks[2]
            elif accounts[loser]["trophies"] > 449 and accounts[loser]["trophies"] < 599 :
                accounts[loser]["rank"] = ranks[3]
            elif accounts[loser]["trophies"] > 749 and accounts[loser]["trophies"] < 899 :
                accounts[loser]["rank"] = ranks[4]
            elif accounts[loser]["trophies"] > 899 and accounts[loser]["trophies"] < 1049 :
                accounts[loser]["rank"] = ranks[5]
            elif accounts[loser]["trophies"] > 1049 and accounts[loser]["trophies"] < 1199 :
                accounts[loser]["rank"] = ranks[6]

            save_accounts()

            await bot.send_message(winner, f"🏆 You won! {trophies_won} trophies")
            await bot.send_message(loser, f"💔 You lost! {trophies_lost} trophies")

        else:
            await bot.send_message(user_id, "❗ Conflicting results. Match cancelled.")
            await bot.send_message(opponent_id, "❗ Conflicting results. Match cancelled.")

            # Cleanup
        del active_games[user_id]
        del active_games[opponent_id]
        user_states[user_id] = None
        user_states[opponent_id] = None

    elif message.text == "Decline match":
        if user_id not in current_matches:
            await bot.send_message(message.chat.id, f"There is no match")
        else:
            challenger_id = current_matches.pop(user_id)
            await bot.send_message(message.chat.id, "❌ Match declined.")
            await bot.send_message(
                challenger_id,
                f"😕 {accounts[user_id]['username']} declined your match request."
            )



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
