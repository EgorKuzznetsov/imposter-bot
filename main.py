import os
import random
from dataclasses import dataclass
from typing import Dict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

THEMES = {
    "Кафе": ["Кофе", "Чай", "Круассан", "Пицца", "Меню"],
    "Школа": ["Доска", "Мел", "Учебник", "Звонок", "Рюкзак"],
}

BRAWL = ["Shelly", "Colt", "Spike", "Crow", "Leon", "Jessie", "Nita", "Bo", "Poco"]

@dataclass
class Game:
    theme: str = ""
    players: int = 0
    spy: int = 0
    word: str = ""
    current: int = 1

games: Dict[int, Game] = {}

def themes_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Кафе ☕", callback_data="theme:Кафе")],
        [InlineKeyboardButton("Школа 🎒", callback_data="theme:Школа")],
        [InlineKeyboardButton("Brawl Stars ⭐", callback_data="theme:BRAWL")]
    ])

def players_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(str(i), callback_data=f"players:{i}") for i in range(3, 7)]
    ])

def show_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Показать", callback_data="show")]])

def ok_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Ок", callback_data="ok")]])

async def game_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    games[update.effective_chat.id] = Game()
    await update.message.reply_text("Выбери тему 👇", reply_markup=themes_kb())

async def on_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    game = games[q.message.chat_id]
    game.theme = q.data.split(":")[1]
    await q.edit_message_text("Выбери количество игроков", reply_markup=players_kb())

async def on_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    game = games[q.message.chat_id]
    game.players = int(q.data.split(":")[1])
    game.spy = random.randint(1, game.players)
    game.word = random.choice(BRAWL if game.theme == "BRAWL" else THEMES[game.theme])
    game.current = 1
    await q.edit_message_text("Игрок 1: нажми «Показать»", reply_markup=show_kb())

async def on_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    game = games[q.message.chat_id]
    text = "🕵️ ТЫ — ШПИОН" if game.current == game.spy else f"✅ Твоё слово: {game.word}"
    await q.edit_message_text(text, reply_markup=ok_kb())

async def on_ok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.delete()
    game = games[q.message.chat_id]
    game.current += 1
    if game.current <= game.players:
        await context.bot.send_message(
            q.message.chat_id,
            f"Игрок {game.current}: нажми «Показать»",
            reply_markup=show_kb()
        )
    else:
        await context.bot.send_message(q.message.chat_id, "✅ Все роли выданы!")

def main():
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("game", game_cmd))
    app.add_handler(CallbackQueryHandler(on_theme, pattern="^theme:"))
    app.add_handler(CallbackQueryHandler(on_players, pattern="^players:"))
    app.add_handler(CallbackQueryHandler(on_show, pattern="^show$"))
    app.add_handler(CallbackQueryHandler(on_ok, pattern="^ok$"))

    app.run_polling()

if __name__ == "__main__":
    main()
