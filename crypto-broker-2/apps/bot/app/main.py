import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token or token == "replace_me":
        print("TELEGRAM_BOT_TOKEN is not configured; bot stopped.")
        return
    bot = Bot(token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start(message: Message):
        url = os.getenv("TELEGRAM_WEBAPP_URL", "")
        if not url:
            await message.answer("Mini App URL is not configured.")
            return
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Open CryptoBroker", web_app=WebAppInfo(url=url))
        ]])
        await message.answer("Welcome to CryptoBroker.", reply_markup=keyboard)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
