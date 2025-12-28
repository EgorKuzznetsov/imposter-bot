import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import Forbidden
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes


# =========================
# ТЕМЫ + СЛОВА
# =========================
THEMES: Dict[str, List[str]] = {
    "Кафе": [
        "Кофе", "Чай", "Капучино", "Латте", "Американо", "Эспрессо", "Раф", "Мокка",
        "Какао", "Лимонад", "Смузи", "Милкшейк",
        "Круассан", "Маффин", "Чизкейк", "Тирамису", "Эклер", "Пончик", "Пирожное",
        "Меню", "Счёт", "Чаевые", "Заказ",
        "Официант", "Бариста", "Повар", "Кассир",
        "Чашка", "Блюдце", "Ложка", "Салфетка", "Поднос",
        "Столик", "Стул", "Терраса", "Витрина", "Wi-Fi"
    ],
    "Школа": [
        "Доска", "Мел", "Маркер", "Учебник", "Тетрадь", "Дневник",
        "Рюкзак", "Пенал", "Ручка", "Карандаш", "Ластик", "Линейка",
        "Урок", "Перемена", "Звонок", "Домашка", "Контрольная", "Экзамен",
        "Учитель", "Директор", "Одноклассник", "Класс", "Парта",
        "Коридор", "Кабинет", "Спортзал", "Столовая", "Библиотека"
    ],
    "Дом": [
        "Диван", "Кресло", "Стул", "Стол", "Шкаф", "Комод",
        "Кровать", "Подушка", "Одеяло", "Плед",
        "Телевизор", "Пульт", "Лампа", "Люстра",
        "Окно", "Шторы", "Дверь",
        "Холодильник", "Микроволновка", "Плита", "Чайник",
        "Сковородка", "Кастрюля",
        "Ванная", "Душ", "Полотенце", "Мыло", "Шампунь"
    ],
    "Улица": [
        "Дорога", "Тротуар", "Асфальт", "Лужа", "Пешеход",
        "Машина", "Автобус", "Трамвай", "Метро", "Такси",
        "Светофор", "Переход", "Знак", "Перекрёсток",
        "Фонарь", "Лавочка", "Урна", "Остановка",
        "Двор", "Подъезд", "Парк", "Аллея", "Площадка"
    ],
    "Путешествия": [
        "Самолёт", "Аэропорт", "Посадка", "Регистрация", "Багаж",
        "Билет", "Паспорт", "Виза", "Контроль",
        "Чемодан", "Рюкзак", "Карта", "Навигатор",
        "Поезд", "Вагон", "Купе", "Перрон",
        "Отель", "Ресепшен", "Номер", "Бронь",
        "Экскурсия", "Сувенир", "Пляж", "Море"
    ],
}

# =========================
# BRAWL STARS
# =========================
BRAWL = [
    "Шелли", "Кольт", "Спайк", "Ворон", "Леон", "Джесси", "Нита", "Бо", "Поко",
    "Эль примо", "Френк", "8-Бит", "Брок", "Эдгар", "Пайпер", "Мортис",
    "Мистер пи", "Пенни", "Пем", "Беа", "Эмз", "Тик", "Джин", "Барли",
    "Диномайк", "Булл", "Роза", "Деррил", "Гавс", "Вольт", "Сенди", "Тара",
    "Кит", "Спраут", "Макс", "Фенг",
]


# =========================
# СОСТОЯНИЯ
# =========================
@dataclass
class LocalGame:
    theme: str = ""
    players: int = 0
    spy_index: int = 0
    word: str = ""
    current_player: int = 1


@dataclass
class OnlineLobby:
    owner_id: int
    theme: Optional[str] = None
    players_target: int = 4
    players: List[int] = field(default_factory=list)     # user_id

    started: bool = False
    spy_id: Optional[int] = None
    word: Optional[str] = None

    voting_active: bool = False
    votes: Dict[int, int] = field(default_factory=dict)  # voter_id -> target_id


LOCAL_GAMES: Dict[int, LocalGame] = {}
ONLINE_LOBBY: Dict[int, OnlineLobby] = {}


# =========================
# КЛАВИАТУРЫ
# =========================
def kb_mode():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 На одном телефоне", callback_data="mode:local")],
        [InlineKeyboardButton("🌐 Онлайн в группе", callback_data="mode:online")],
    ])

def kb_themes(prefix: str):
    rows = []
    for t in THEMES.keys():
        rows.append([InlineKeyboardButton(t, callback_data=f"{prefix}:{t}")])
    rows.append([InlineKeyboardButton("Brawl Stars ⭐", callback_data=f"{prefix}:BRAWL")])
    return InlineKeyboardMarkup(rows)

def kb_players(prefix: str, min_n: int, max_n: int):
    row = [InlineKeyboardButton(str(i), callback_data=f"{prefix}:{i}") for i in range(min_n, max_n + 1)]
    return InlineKeyboardMarkup([row])

def kb_show():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Показать", callback_data="local_show")]])

def kb_ok():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Ок", callback_data="local_ok")]])

def kb_lobby():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Присоединиться", callback_data="online_join")],
        [InlineKeyboardButton("➖ Выйти", callback_data="online_leave")],
        [InlineKeyboardButton("✅ Начать", callback_data="online_start")],
        [InlineKeyboardButton("🛑 Закрыть лобби", callback_data="online_close")],
    ])

def kb_vote_start():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗳 Начать голосование", callback_data="online_vote_start")],
    ])

def display_name(u) -> str:
    if u.username:
        return f"@{u.username}"
    return u.first_name or "Игрок"


# =========================
# ТЕКСТ ЛОББИ
# =========================
def lobby_text(chat_id: int) -> str:
    lobby = ONLINE_LOBBY[chat_id]
    theme_name = "Brawl Stars ⭐" if lobby.theme == "BRAWL" else (lobby.theme or "—")
    return (
        f"🌐 Онлайн-лобби\n"
        f"Тема: {theme_name}\n"
        f"Игроки: {len(lobby.players)}/{lobby.players_target}\n\n"
        f"Нажмите «Присоединиться». Когда все собрались — «Начать».\n"
        f"Важно: каждый игрок должен открыть бота в личке и нажать /start (один раз), иначе роль не придёт."
    )


# =========================
# КОМАНДЫ
# =========================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот «Шпион».\n\n"
        "Команды:\n"
        "/game — начать (выбор режима)\n"
        "/stop — остановить\n\n"
        "Для онлайн-режима: каждый игрок должен открыть меня в личке и нажать /start один раз."
    )

async def cmd_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери режим 👇", reply_markup=kb_mode())

async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    LOCAL_GAMES.pop(chat_id, None)
    ONLINE_LOBBY.pop(chat_id, None)
    await update.message.reply_text("Остановлено. Чтобы начать заново: /game")


# =========================
# ВЫБОР РЕЖИМА
# =========================
async def on_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    mode = q.data.split(":", 1)[1]
    chat = q.message.chat
    chat_id = chat.id

    if mode == "local":
        LOCAL_GAMES[chat_id] = LocalGame()
        await q.edit_message_text("📱 Режим: на одном телефоне.\nВыбери тему:", reply_markup=kb_themes("local_theme"))
        return

    # online
    if chat.type not in ("group", "supergroup"):
        await q.edit_message_text(
            "🌐 Онлайн-режим работает в ГРУППЕ.\n"
            "Создайте группу, добавьте туда бота и вызовите /game в группе."
        )
        return

    ONLINE_LOBBY[chat_id] = OnlineLobby(owner_id=q.from_user.id)
    await q.edit_message_text("🌐 Режим: онлайн.\nВыбери тему:", reply_markup=kb_themes("online_theme"))


# =========================
# ЛОКАЛЬНЫЙ РЕЖИМ
# =========================
async def on_local_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = LOCAL_GAMES.get(chat_id) or LocalGame()
    LOCAL_GAMES[chat_id] = game

    game.theme = q.data.split(":", 1)[1]
    await q.edit_message_text("Выбери количество игроков:", reply_markup=kb_players("local_players", 2, 10))

async def on_local_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = LOCAL_GAMES.get(chat_id)
    if not game:
        await q.edit_message_text("Нет активной игры. /game")
        return

    n = int(q.data.split(":", 1)[1])
    game.players = n
    game.spy_index = random.randint(1, n)

    if game.theme == "BRAWL":
        game.word = random.choice(BRAWL)
    else:
        game.word = random.choice(THEMES[game.theme])

    game.current_player = 1
    await q.edit_message_text("Игрок 1: нажми «Показать»", reply_markup=kb_show())

async def on_local_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = LOCAL_GAMES.get(chat_id)
    if not game or game.players <= 0:
        await q.edit_message_text("Нет активной раздачи ролей. /game")
        return

    if game.current_player == game.spy_index:
        text = "🕵️ ТЫ — ШПИОН"
    else:
        text = f"✅ Твоё слово: {game.word}"

    await q.edit_message_text(text, reply_markup=kb_ok())

async def on_local_ok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = LOCAL_GAMES.get(chat_id)

    try:
        await q.message.delete()
    except:
        pass

    if not game:
        return

    game.current_player += 1
    if game.current_player <= game.players:
        await context.bot.send_message(chat_id, f"Игрок {game.current_player}: нажми «Показать»", reply_markup=kb_show())
    else:
        await context.bot.send_message(chat_id, "🎉 Все роли выданы! Играйте 🙂")


# =========================
# ОНЛАЙН РЕЖИМ: лобби
# =========================
async def on_online_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id

    lobby = ONLINE_LOBBY.get(chat_id)
    if not lobby:
        await q.edit_message_text("Лобби не найдено. /game")
        return

    lobby.theme = q.data.split(":", 1)[1]
    await q.edit_message_text("Сколько игроков будет в игре?", reply_markup=kb_players("online_players", 3, 10))

async def on_online_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id

    lobby = ONLINE_LOBBY.get(chat_id)
    if not lobby:
        await q.edit_message_text("Лобби не найдено. /game")
        return

    lobby.players_target = int(q.data.split(":", 1)[1])

    if lobby.owner_id not in lobby.players:
        lobby.players.append(lobby.owner_id)

    # показываем лобби
    await q.edit_message_text(lobby_text(chat_id), reply_markup=kb_lobby())

async def on_online_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    lobby = ONLINE_LOBBY.get(chat_id)
    if not lobby or lobby.started:
        return

    uid = q.from_user.id
    if uid not in lobby.players:
        lobby.players.append(uid)

    await q.edit_message_text(lobby_text(chat_id), reply_markup=kb_lobby())

async def on_online_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    lobby = ONLINE_LOBBY.get(chat_id)
    if not lobby or lobby.started:
        return

    uid = q.from_user.id
    if uid in lobby.players:
        lobby.players.remove(uid)

    await q.edit_message_text(lobby_text(chat_id), reply_markup=kb_lobby())

async def on_online_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    lobby = ONLINE_LOBBY.get(chat_id)
    if not lobby:
        return

    if q.from_user.id != lobby.owner_id:
        await q.answer("Закрыть лобби может только создатель.", show_alert=True)
        return

    ONLINE_LOBBY.pop(chat_id, None)
    await q.edit_message_text("Лобби закрыто. /game чтобы создать новое.")


# =========================
# ОНЛАЙН РЕЖИМ: старт + голосование
# =========================
def kb_vote(lobby: OnlineLobby) -> InlineKeyboardMarkup:
    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []
    for uid in lobby.players:
        # показываем имена в кнопках
        name = lobby_display_name(uid, lobby)
        row.append(InlineKeyboardButton(name, callback_data=f"online_vote:{uid}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

def lobby_display_name(uid: int, lobby: OnlineLobby) -> str:
    # пытаемся красиво показать: @username или first_name
    # если нет — часть id
    return lobby._names.get(uid) if hasattr(lobby, "_names") and uid in lobby._names else f"id:{str(uid)[-4:]}"

async def on_online_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    lobby = ONLINE_LOBBY.get(chat_id)
    if not lobby or lobby.started:
        return

    if q.from_user.id != lobby.owner_id:
        await q.answer("Начать игру может только создатель.", show_alert=True)
        return

    if len(lobby.players) < 3:
        await q.answer("Нужно минимум 3 игрока.", show_alert=True)
        return

    if len(lobby.players) < lobby.players_target:
        await q.answer("Соберите всех игроков или уменьшите количество.", show_alert=True)
        return

    # сохраняем имена игроков (чтобы в голосовании были не id)
    if not hasattr(lobby, "_names"):
        lobby._names = {}
    for uid in lobby.players:
        # имя берём хотя бы от того, кто нажимал — остальные могут быть неизвестны,
        # но обычно Telegram отдаёт from_user при join, так что будет ок.
        # Если нет — оставим короткий id.
        pass
    # Обновим имя текущего пользователя
    lobby._names[q.from_user.id] = display_name(q.from_user)

    # выбрать слово и шпиона
    lobby.started = True
    lobby.voting_active = False
    lobby.votes.clear()

    lobby.spy_id = random.choice(lobby.players)
    if lobby.theme == "BRAWL":
        lobby.word = random.choice(BRAWL)
    else:
        lobby.word = random.choice(THEMES[lobby.theme])

    # раздать роли в личку
    not_ready = []
    for uid in lobby.players:
        try:
            if uid == lobby.spy_id:
                await context.bot.send_message(chat_id=uid, text="🕵️ ТЫ — ШПИОН")
            else:
                label = "Персонаж" if lobby.theme == "BRAWL" else "Слово"
                await context.bot.send_message(chat_id=uid, text=f"✅ {label}: {lobby.word}")
        except Forbidden:
            not_ready.append(uid)
        except:
            not_ready.append(uid)

    if not_ready:
        # Надёжно сообщаем в группу (НОВЫМ сообщением), а не edit
        lobby.started = False
        lobby.spy_id = None
        lobby.word = None
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Не всем удалось отправить роль в личку.\n"
                 "Эти игроки должны открыть бота в личке и нажать /start.\n"
                 "Потом создайте игру заново.",
        )
        return

    # ВАЖНО: НЕ редактируем лобби, а шлём новое сообщение в группу
    await context.bot.send_message(
        chat_id=chat_id,
        text="✅ Роли выданы в личные сообщения!\nНачинайте обсуждение в группе 🙂\n\n"
             "Когда будете готовы — нажмите «Начать голосование».",
        reply_markup=kb_vote_start()
    )

    # Можно оставить лобби как есть, или попытаться отключить кнопки (не критично)
    try:
        await q.edit_message_reply_markup(reply_markup=None)
    except:
        pass


async def on_online_vote_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    lobby = ONLINE_LOBBY.get(chat_id)
    if not lobby or not lobby.started:
        await q.answer("Игра не запущена.", show_alert=True)
        return

    if lobby.voting_active:
        await q.answer("Голосование уже идёт.", show_alert=True)
        return

    lobby.voting_active = True
    lobby.votes.clear()

    await q.edit_message_text(
        "🗳 Голосование началось!\n"
        "Нажмите на игрока, которого вы подозреваете.\n"
        "Каждый может проголосовать 1 раз.\n\n"
        f"Проголосовали: 0/{len(lobby.players)}",
        reply_markup=kb_vote(lobby)
    )

async def on_online_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    lobby = ONLINE_LOBBY.get(chat_id)
    if not lobby or not lobby.voting_active:
        await q.answer("Голосование не активно.", show_alert=True)
        return

    voter = q.from_user.id
    if voter not in lobby.players:
        await q.answer("Вы не в этой игре.", show_alert=True)
        return

    target = int(q.data.split(":", 1)[1])
    if target not in lobby.players:
        await q.answer("Неверный выбор.", show_alert=True)
        return

    lobby.votes[voter] = target

    total = len(lobby.players)
    done = len(lobby.votes)

    # обновим сообщение голосования
    try:
        await q.edit_message_text(
            "🗳 Голосование идёт!\n"
            "Нажмите на игрока, которого вы подозреваете.\n"
            "Каждый может проголосовать 1 раз.\n\n"
            f"Проголосовали: {done}/{total}",
            reply_markup=kb_vote(lobby)
        )
    except:
        pass

    if done >= total:
        await finish_voting(chat_id, context)

async def finish_voting(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    lobby = ONLINE_LOBBY.get(chat_id)
    if not lobby:
        return

    lobby.voting_active = False

    # подсчёт голосов
    counts: Dict[int, int] = {}
    for target in lobby.votes.values():
        counts[target] = counts.get(target, 0) + 1

    max_votes = max(counts.values())
    top = [uid for uid, c in counts.items() if c == max_votes]
    eliminated = random.choice(top)

    eliminated_name = lobby_display_name(eliminated, lobby)
    spy_name = lobby_display_name(lobby.spy_id, lobby) if lobby.spy_id else "шпион"

    if eliminated == lobby.spy_id:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Большинство выбрало {eliminated_name}.\nЭто был ШПИОН! Мирные выигрывают 🎉"
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Большинство выбрало {eliminated_name}.\nЭто НЕ шпион.\nШпион выигрывает! 🕵️🎉 (Шпион: {spy_name})"
        )

    ONLINE_LOBBY.pop(chat_id, None)


# =========================
# MAIN
# =========================
def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set in Railway Variables")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("game", cmd_game))
    app.add_handler(CommandHandler("stop", cmd_stop))

    app.add_handler(CallbackQueryHandler(on_mode, pattern=r"^mode:"))

    # local
    app.add_handler(CallbackQueryHandler(on_local_theme, pattern=r"^local_theme:"))
    app.add_handler(CallbackQueryHandler(on_local_players, pattern=r"^local_players:"))
    app.add_handler(CallbackQueryHandler(on_local_show, pattern=r"^local_show$"))
    app.add_handler(CallbackQueryHandler(on_local_ok, pattern=r"^local_ok$"))

    # online
    app.add_handler(CallbackQueryHandler(on_online_theme, pattern=r"^online_theme:"))
    app.add_handler(CallbackQueryHandler(on_online_players, pattern=r"^online_players:"))
    app.add_handler(CallbackQueryHandler(on_online_join, pattern=r"^online_join$"))
    app.add_handler(CallbackQueryHandler(on_online_leave, pattern=r"^online_leave$"))
    app.add_handler(CallbackQueryHandler(on_online_start, pattern=r"^online_start$"))
    app.add_handler(CallbackQueryHandler(on_online_close, pattern=r"^online_close$"))

    # voting
    app.add_handler(CallbackQueryHandler(on_online_vote_start, pattern=r"^online_vote_start$"))
    app.add_handler(CallbackQueryHandler(on_online_vote, pattern=r"^online_vote:"))

    app.run_polling()

if __name__ == "__main__":
    main()
