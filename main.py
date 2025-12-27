import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import Forbidden
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# =========================
# МЕГА ТЕМЫ + СЛОВА
# =========================
THEMES: Dict[str, List[str]] = {
    "Кафе": [
        "Кофе", "Чай", "Капучино", "Латте", "Американо", "Эспрессо", "Раф", "Мокка",
        "Какао", "Горячий шоколад", "Матча", "Лимонад", "Смузи", "Милкшейк",
        "Круассан", "Маффин", "Чизкейк", "Тирамису", "Эклер", "Пончик", "Пирожное",
        "Торт", "Печенье", "Вафли", "Блины", "Сэндвич", "Пицца", "Салат",
        "Меню", "Счёт", "Чаевые", "Заказ", "Доставка", "Самовывоз",
        "Официант", "Бариста", "Повар", "Кассир", "Гость", "Очередь",
        "Чашка", "Блюдце", "Ложка", "Вилка", "Нож", "Салфетка", "Поднос",
        "Столик", "Стул", "Диванчик", "Витрина", "Терраса", "Музыка", "Wi-Fi"
    ],
    "Школа": [
        "Доска", "Мел", "Маркер", "Губка", "Учебник", "Тетрадь", "Дневник",
        "Рюкзак", "Пенал", "Ручка", "Карандаш", "Ластик", "Линейка", "Циркуль",
        "Урок", "Перемена", "Звонок", "Домашка", "Контрольная", "Экзамен", "Тест",
        "Учитель", "Директор", "Завуч", "Одноклассник", "Класс", "Парта", "Стул",
        "Коридор", "Кабинет", "Спортзал", "Раздевалка", "Столовая", "Библиотека",
        "Математика", "Русский язык", "История", "Биология", "Химия", "Физика",
        "География", "Информатика", "Литература", "Музыка", "ИЗО", "Физкультура"
    ],
    "Дом": [
        "Диван", "Кресло", "Стул", "Стол", "Шкаф", "Комод", "Полка",
        "Кровать", "Подушка", "Одеяло", "Простыня", "Плед", "Матрас",
        "Телевизор", "Пульт", "Колонка", "Лампа", "Люстра", "Розетка",
        "Ковёр", "Зеркало", "Окно", "Шторы", "Дверь", "Ключ", "Замок",
        "Холодильник", "Микроволновка", "Плита", "Духовка", "Чайник",
        "Сковородка", "Кастрюля", "Тарелка", "Чашка", "Ложка", "Вилка", "Нож",
        "Ванная", "Душ", "Ванна", "Полотенце", "Мыло", "Шампунь", "Фен",
        "Зубная щётка", "Порошок", "Пылесос", "Швабра", "Ведро"
    ],
    "Улица": [
        "Дорога", "Тротуар", "Асфальт", "Яма", "Лужа", "Пешеход",
        "Машина", "Автобус", "Трамвай", "Метро", "Такси", "Велосипед", "Самокат",
        "Светофор", "Пешеходный переход", "Знак", "Перекрёсток", "Поворот",
        "Фонарь", "Лавочка", "Урна", "Остановка", "Киоск", "Витрина",
        "Двор", "Подъезд", "Лифт", "Лестница", "Парк", "Аллея", "Дерево",
        "Детская площадка", "Качели", "Горка", "Песочница", "Собака", "Кошка"
    ],
    "Путешествия": [
        "Самолёт", "Аэропорт", "Посадка", "Регистрация", "Багаж", "Ручная кладь",
        "Билет", "Паспорт", "Виза", "Контроль", "Таможня", "Очередь",
        "Чемодан", "Рюкзак", "Сумка", "Навигатор", "Карта", "Гид",
        "Поезд", "Вагон", "Купе", "Плацкарт", "Проводник", "Перрон",
        "Отель", "Ресепшен", "Номер", "Ключ-карта", "Завтрак", "Бронь",
        "Экскурсия", "Музей", "Памятник", "Сувенир", "Фото", "Пляж", "Море",
        "Шезлонг", "Солнцезащитный крем", "Очки"
    ],
    "Спорт": [
        "Мяч", "Стадион", "Поле", "Трибуны", "Команда", "Игрок", "Тренер",
        "Судья", "Свисток", "Матч", "Гол", "Очко", "Турнир", "Кубок",
        "Форма", "Кроссовки", "Разминка", "Тренировка", "Растяжка",
        "Фитнес", "Зал", "Гантели", "Штанга", "Тренажёр", "Коврик",
        "Бассейн", "Плавание", "Дорожка", "Старт", "Финиш",
        "Бег", "Марафон", "Йога", "Пилатес", "Скакалка"
    ],
    "Работа": [
        "Офис", "Кабинет", "Рабочий стол", "Компьютер", "Монитор",
        "Клавиатура", "Мышка", "Принтер", "Сканер", "Папка", "Документ",
        "Письмо", "Почта", "Звонок", "Встреча", "Совещание",
        "Проект", "Задача", "Дедлайн", "Отчёт", "Презентация",
        "Клиент", "Договор", "Подпись", "Печать", "Счёт",
        "Перерыв", "Кофе-брейк", "Кухня", "Коллега", "Начальник"
    ],
    "Природа": [
        "Лес", "Поляна", "Дерево", "Куст", "Трава", "Цветок",
        "Река", "Озеро", "Море", "Водопад", "Пляж", "Песок",
        "Гора", "Холм", "Пещера", "Туман", "Роса", "Снег",
        "Дождь", "Гроза", "Ветер", "Солнце", "Облако", "Радуга",
        "Птица", "Рыба", "Лиса", "Волк", "Медведь", "Заяц", "Белка"
    ],
}

# =========================
# BRAWL STARS (как ты попросил)
# =========================
BRAWL = [
    "Шелли", "Кольт", "Спайк", "Ворон", "Леон", "Джесси", "Нита", "Бо", "Поко",
    "Эль примо", "Френк", "8-Бит", "Брок", "Эдгар", "Пайпер", "Мортис",
    "Мистер пи", "Пенни", "Пем", "Беа", "Эмз", "Тик", "Джин", "Барли",
    "Диномайк", "Булл", "Роза", "Деррил", "Гавс", "Вольт", "Сенди", "Тара",
    "Кит", "Спраут", "Макс", "Фенг",
]

# =========================
# СТЕЙТЫ
# =========================
@dataclass
class LocalGame:
    theme: str = ""
    players: int = 0
    spy_index: int = 0  # 1..players
    word: str = ""
    current_player: int = 1

@dataclass
class OnlineLobby:
    owner_id: int
    theme: Optional[str] = None
    players_target: int = 4
    players: List[int] = field(default_factory=list)  # user_id list
    started: bool = False
    spy_id: Optional[int] = None
    word: Optional[str] = None
    not_ready: Set[int] = field(default_factory=set)  # users бот не смог написать в личку

LOCAL_GAMES: Dict[int, LocalGame] = {}         # chat_id -> LocalGame
ONLINE_LOBBY: Dict[int, OnlineLobby] = {}      # group_chat_id -> OnlineLobby


# =========================
# КЛАВИАТУРЫ
# =========================
def kb_mode():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 На одном телефоне", callback_data="mode:local")],
        [InlineKeyboardButton("🌐 Онлайн в группе", callback_data="mode:online")],
    ])

def kb_themes(prefix: str):
    # prefix: local_theme / online_theme
    rows = []
    for t in THEMES.keys():
        rows.append([InlineKeyboardButton(t, callback_data=f"{prefix}:{t}")])
    rows.append([InlineKeyboardButton("Brawl Stars ⭐", callback_data=f"{prefix}:BRAWL")])
    return InlineKeyboardMarkup(rows)

def kb_players(prefix: str, min_n: int, max_n: int):
    # одна строка кнопок (можно расширить на 2 строки при желании)
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

def mention_user_id(user_id: int) -> str:
    return f"<a href='tg://user?id={user_id}'>игрок</a>"


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
# ОНЛАЙН РЕЖИМ (ГРУППА + ЛИЧКА)
# =========================
def lobby_text(chat_id: int) -> str:
    lobby = ONLINE_LOBBY[chat_id]
    theme_name = "Brawl Stars ⭐" if lobby.theme == "BRAWL" else (lobby.theme or "—")
    players_count = len(lobby.players)
    return (
        f"🌐 Онлайн-лобби\n"
        f"Тема: {theme_name}\n"
        f"Игроки: {players_count}/{lobby.players_target}\n\n"
        f"Нажмите «Присоединиться». Когда все собрались — «Начать».\n"
        f"Важно: каждый игрок должен открыть бота в личке и нажать /start (один раз), иначе роль не придёт."
    )

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

    # владелец автоматически добавляется
    if lobby.owner_id not in lobby.players:
        lobby.players.append(lobby.owner_id)

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

    # закрыть может только создатель
    if q.from_user.id != lobby.owner_id:
        await q.answer("Закрыть лобби может только создатель.", show_alert=True)
        return

    ONLINE_LOBBY.pop(chat_id, None)
    await q.edit_message_text("Лобби закрыто. /game чтобы создать новое.")

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

    # выбрать слово и шпиона
    lobby.started = True
    lobby.spy_id = random.choice(lobby.players)

    if lobby.theme == "BRAWL":
        lobby.word = random.choice(BRAWL)
    else:
        lobby.word = random.choice(THEMES[lobby.theme])

    lobby.not_ready.clear()

    # раздать роли в личку
    for uid in lobby.players:
        try:
            if uid == lobby.spy_id:
                await context.bot.send_message(chat_id=uid, text="🕵️ ТЫ — ШПИОН")
            else:
                label = "Персонаж" if lobby.theme == "BRAWL" else "Слово"
                await context.bot.send_message(chat_id=uid, text=f"✅ {label}: {lobby.word}")
        except Forbidden:
            lobby.not_ready.add(uid)
        except:
            lobby.not_ready.add(uid)

    if lobby.not_ready:
        # показать, что кто-то не открыл личку
        await q.edit_message_text(
            "⚠️ Не всем удалось отправить роль в личку.\n"
            "Эти игроки должны открыть бота в личке и нажать /start, потом создайте игру заново.\n\n"
            "Подсказка: просто пусть каждый откроет бота, нажмёт Start — и всё.",
            reply_markup=kb_lobby()
        )
        lobby.started = False
        lobby.spy_id = None
        lobby.word = None
        return

    # успех
    await q.edit_message_text(
        "✅ Роли выданы в личные сообщения!\n"
        "Начинайте обсуждение в группе 🙂",
        reply_markup=None
    )


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

    app.run_polling()

if __name__ == "__main__":
    main()
