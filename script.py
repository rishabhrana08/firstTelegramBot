import os
import logging
import requests
import asyncio
from telegram import Bot
from datetime import datetime, time

# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Whale Alert API (Example: Replace with actual API integration)
API_ENDPOINTS = {
    "ethereum": "https://api.whale-alert.io/v1/transactions?blockchain=ethereum",
    "bsc": "https://api.whale-alert.io/v1/transactions?blockchain=bsc",
    "solana": "https://api.whale-alert.io/v1/transactions?blockchain=solana",
    "ripple": "https://api.whale-alert.io/v1/transactions?blockchain=ripple",
}

# Filtering Criteria
MIN_TRANSACTION_AMOUNT = 15000  # Minimum $15K
MIN_WIN_RATE = 90  # Minimum 90% win rate

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WhaleBot")

async def send_telegram_alert(message):
    """Sends a message to the Telegram group."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

async def fetch_whale_transactions():
    """Fetches whale transactions and filters them based on criteria."""
    for blockchain, url in API_ENDPOINTS.items():
        response = requests.get(url, headers={"Authorization": f"Bearer {os.getenv('WHALE_ALERT_API_KEY')}"})
        if response.status_code == 200:
            data = response.json()
            for tx in data.get("transactions", []):
                amount_usd = tx.get("amount_usd", 0)
                win_rate = tx.get("win_rate", 0)  # Assuming win rate is provided
                if amount_usd >= MIN_TRANSACTION_AMOUNT and win_rate >= MIN_WIN_RATE:
                    message = (f"🔥 Whale Alert on {blockchain.upper()} 🔥\n"
                               f"Amount: ${amount_usd}\n"
                               f"Win Rate: {win_rate}%\n"
                               f"Transaction: {tx.get('hash')}")
                    await send_telegram_alert(message)
        else:
            logger.error(f"Failed to fetch data from {blockchain.upper()}")

async def scheduled_task():
    """Runs the bot only between 6 AM - 2 AM."""
    while True:
        now = datetime.now().time()
        if time(6, 0) <= now <= time(2, 0):
            await fetch_whale_transactions()
        await asyncio.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    asyncio.run(scheduled_task())
