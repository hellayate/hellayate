import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
import logging
import os

# --- НАСТРОЙКИ ---
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # вставь сюда токен от BotFather
ADMIN_ID = 123456789  # твой Telegram user ID (узнать можно через @userinfobot)

# --- ЛОГИ ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# --- КНОПКИ ---
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎬 Заказать монтаж", callback_data="order")
    kb.button(text="💸 Прайс", callback_data="price")
    kb.button(text="📞 Контакты", callback_data="contacts")
    kb.adjust(1)
    return kb.as_markup()

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Привет! Я бот для заказа видеомонтажа от <b>hellayate</b>.\n\nВыбери, что тебя интересует:",
        reply_markup=main_menu())

# --- ОБРАБОТКА КНОПОК ---
@dp.callback_query(F.data == "price")
async def show_price(callback: CallbackQuery):
    text = (
        "<b>💸 Прайс-лист:</b>\n\n"
        "• TikTok / Reels — от 5$\n"
        "• YouTube (до 10 мин) — до 15$\n"
        "• YouTube (10+ мин) — от 15$\n"
        "• Доп. эффекты, субтитры, графика — обсуждается отдельно"
    )
    await callback.message.edit_text(text, reply_markup=main_menu())

@dp.callback_query(F.data == "contacts")
async def show_contacts(callback: CallbackQuery):
    text = (
        "<b>📞 Контакты:</b>\n\n"
        "• Telegram: @hellayate\n"
        "• WhatsApp: wa.me/123456789\n"
        "• Instagram: instagram.com/hellayate"
    )
    await callback.message.edit_text(text, reply_markup=main_menu())

# --- ЗАКАЗ ---
user_orders = {}

@dp.callback_query(F.data == "order")
async def start_order(callback: CallbackQuery):
    user_orders[callback.from_user.id] = {}
    await callback.message.answer("Какой тип видео? (YouTube / TikTok / Reels)")

@dp.message(F.text)
async def collect_order(message: Message):
    uid = message.from_user.id
    if uid not in user_orders:
        return

    order = user_orders[uid]

    if "type" not in order:
        order["type"] = message.text
        await message.answer("Какая длительность? (в минутах)")
    elif "duration" not in order:
        order["duration"] = message.text
        await message.answer("Есть ли материалы? (ссылки или "нет")")
    elif "materials" not in order:
        order["materials"] = message.text
        await message.answer("Есть пожелания по монтажу? (если нет — напиши 'нет')")
    elif "notes" not in order:
        order["notes"] = message.text
        await message.answer("✅ Спасибо! Заявка отправлена.")

        text = (
            f"<b>📥 Новый заказ:</b>\n"
            f"👤 @{message.from_user.username or message.from_user.full_name}\n"
            f"📹 Тип: {order['type']}\n"
            f"⏱ Длительность: {order['duration']}\n"
            f"📎 Материалы: {order['materials']}\n"
            f"📝 Пожелания: {order['notes']}"
        )
        await bot.send_message(ADMIN_ID, text)
        user_orders.pop(uid)

# --- ЗАПУСК ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
