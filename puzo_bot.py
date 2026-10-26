import asyncio
import os
import random
import sqlite3
from datetime import date

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

TOKEN = os.getenv("BOT_TOKEN")  # токен от @BotFather
db = sqlite3.connect("puzo.db")
db.execute("CREATE TABLE IF NOT EXISTS waist (uid INT, day TEXT, cm REAL)")

PROGRAM = [
    "🍳 Завтрак: яичница из 4 яиц, тосты с маслом, какао",
    "🥜 Перекус: горсть орехов + банан + йогурт",
    "🍝 Обед: паста с мясом и сыром, хлеб",
    "🥛 Перекус: молочный коктейль или кефир с мёдом",
    "🍚 Ужин: рис/картошка + курица или рыба + овощи",
    "🍫 На ночь: творог со сгущёнкой (по желанию)",
]

TIPS = [
    "Ешь чаще: 5–6 приёмов пищи вместо трёх.",
    "Пей калорийные напитки: молоко, смузи, какао.",
    "Добавляй масло, орехи и сыр в каждое блюдо.",
    "Спи 8 часов — рост тоже происходит во сне.",
    "Не забывай про базовые упражнения, чтобы набирать не только пузо 😄",
]

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/program"), KeyboardButton(text="/tip")],
        [KeyboardButton(text="/stats")],
    ],
    resize_keyboard=True,
)

dp = Dispatcher()


@dp.message(Command("start"))
async def start(m: Message):
    await m.answer(
        "Привет! Я Пузомер 🍔\n\n"
        "/program — меню на день\n"
        "/waist 95 — записать объём талии (см)\n"
        "/stats — динамика роста\n"
        "/tip — совет",
        reply_markup=kb,
    )


@dp.message(Command("program"))
async def program(m: Message):
    await m.answer("Программа роста на сегодня:\n\n" + "\n".join(PROGRAM))


@dp.message(Command("tip"))
async def tip(m: Message):
    await m.answer("💡 " + random.choice(TIPS))


@dp.message(Command("waist"))
async def waist(m: Message, command: CommandObject):
    try:
        cm = float(command.args.replace(",", "."))
    except (AttributeError, ValueError):
        return await m.answer("Напиши так: /waist 95")
    db.execute(
        "INSERT INTO waist VALUES (?, ?, ?)", (m.from_user.id, date.today().isoformat(), cm)
    )
    db.commit()
    await m.answer(f"Записал: {cm} см ✅")


@dp.message(Command("stats"))
async def stats(m: Message):
    rows = db.execute(
        "SELECT day, cm FROM waist WHERE uid=? ORDER BY day", (m.from_user.id,)
    ).fetchall()
    if not rows:
        return await m.answer("Пока пусто. Добавь замер: /waist 95")
    text = "\n".join(f"{d}: {cm} см" for d, cm in rows[-10:])
    diff = rows[-1][1] - rows[0][1]
    await m.answer(f"{text}\n\nИзменение с начала: {diff:+.1f} см")


async def main():
    await dp.start_polling(Bot(TOKEN))


if __name__ == "__main__":
    asyncio.run(main())
