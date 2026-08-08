"""Telegram Bot for CryptoBroker - aiogram 3 integration."""
import asyncio
import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Finite State Machine for order creation flow
class OrderCreation(StatesGroup):
    """FSM states for order creation workflow."""
    waiting_for_sell_amount = State()
    waiting_for_withdrawal_address = State()
    waiting_for_confirmation = State()


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message):
    """Handle /start command - show welcome message with Mini App button."""
    webapp_url = os.getenv("TELEGRAM_WEBAPP_URL", "https://localhost:3000")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Open CryptoBroker",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Get Quote",
                    callback_data="get_quote",
                )
            ],
        ]
    )
    
    await message.answer(
        "👋 Welcome to **CryptoBroker**!\n\n"
        "Non-custodial OTC routing engine for B2B and closed community.\n\n"
        "✨ Features:\n"
        "• Best rates from multiple liquidity providers\n"
        "• Non-custodial (we don't store your funds)\n"
        "• Fast settlement via OKX/Bybit\n\n"
        "Click the button below to start trading:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "get_quote")
async def handle_get_quote_callback(callback: CallbackQuery, state: FSMContext):
    """Start quote creation flow."""
    await state.clear()
    await callback.message.edit_text(
        "💱 **Create New Quote**\n\n"
        "Enter the amount of USDT you want to exchange to BTC:\n\n"
        "_Example: 1000_",
        parse_mode="Markdown",
    )
    await state.set_state(OrderCreation.waiting_for_sell_amount)


@router.message(OrderCreation.waiting_for_sell_amount)
async def process_sell_amount(message: Message, state: FSMContext):
    """Process sell amount input."""
    try:
        amount = Decimal(message.text.strip())
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Store amount in FSM state
        await state.update_data(sell_amount=float(amount))
        
        await message.answer(
            f"✅ Amount: **{amount} USDT**\n\n"
            "Now enter your **BTC withdrawal address** (TRC20/ERC20):",
            parse_mode="Markdown",
        )
        await state.set_state(OrderCreation.waiting_for_withdrawal_address)
        
    except (ValueError, Exception) as e:
        await message.answer(
            "❌ Invalid amount. Please enter a valid positive number.\n"
            f"Error: {str(e)}\n\n"
            "Try again or /cancel to abort.",
        )


@router.message(OrderCreation.waiting_for_withdrawal_address)
async def process_withdrawal_address(message: Message, state: FSMContext):
    """Process withdrawal address input."""
    address = message.text.strip()
    
    # Basic validation (in production, use proper crypto address validation)
    if len(address) < 26:
        await message.answer(
            "❌ Invalid address. Please enter a valid crypto address.\n"
            "Try again or /cancel to abort.",
        )
        return
    
    # Store address
    await state.update_data(withdrawal_address=address)
    
    # Get stored data
    data = await state.get_data()
    sell_amount = data.get("sell_amount", 0)
    
    # Simulate quote calculation (in production, call API)
    buy_amount = sell_amount * 0.000015  # Example rate
    fee = sell_amount * 0.015  # 1.5% fee
    
    await message.answer(
        f"📋 **Quote Summary**\n\n"
        f"💰 Send: **{sell_amount} USDT**\n"
        f"💵 Receive: **{buy_amount:.6f} BTC**\n"
        f"💸 Fee: **{fee} USDT** (1.5%)\n"
        f"📍 Address: `{address}`\n\n"
        f"_Quote expires in 30 seconds_\n\n"
        "Confirm this order?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Confirm", callback_data="confirm_order"),
                    InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_order"),
                ]
            ]
        ),
        parse_mode="Markdown",
    )
    await state.set_state(OrderCreation.waiting_for_confirmation)


@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    """Confirm and create order."""
    data = await state.get_data()
    
    # In production, call API to create order
    # For now, simulate success
    order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    await callback.message.edit_text(
        f"✅ **Order Created!**\n\n"
        f"Order ID: `{order_id}`\n\n"
        f"Please send **{data['sell_amount']} USDT** to the address shown in Mini App.\n\n"
        f"_Status: AWAITING_PAYMENT_",
        parse_mode="Markdown",
    )
    
    await state.clear()


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Cancel order creation."""
    await callback.message.edit_text("❌ Order cancelled.")
    await state.clear()


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    """Cancel current operation."""
    await state.clear()
    await message.answer("❌ Operation cancelled. Use /start to begin again.")


@router.message(Command("help"))
async def handle_help(message: Message):
    """Show help message."""
    await message.answer(
        "📖 **CryptoBroker Help**\n\n"
        "**Commands:**\n"
        "/start - Open Mini App and start trading\n"
        "/help - Show this help message\n"
        "/cancel - Cancel current operation\n\n"
        "**How it works:**\n"
        "1. Request a quote via Mini App or bot\n"
        "2. Confirm the rate and fee\n"
        "3. Send crypto to provided address\n"
        "4. Receive your coins instantly!",
        parse_mode="Markdown",
    )


async def main():
    """Main bot entry point."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    if not token or token == "replace_me":
        logger.warning(
            "TELEGRAM_BOT_TOKEN is not configured. "
            "Set TELEGRAM_BOT_TOKEN environment variable to run the bot."
        )
        print("\n⚠️  Bot token not configured. To run the bot:")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        print("   export TELEGRAM_WEBAPP_URL='https://your-mini-app-url.com'\n")
        return
    
    bot = Bot(token=token)
    dp = Dispatcher()
    
    # Include routers
    dp.include_router(router)
    
    logger.info("Starting CryptoBroker Telegram Bot...")
    print("\n✅ CryptoBroker Bot is running!")
    print(f"Bot username: {(await bot.get_me()).username}\n")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())

