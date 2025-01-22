import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import Config
from handlers import setup
from logger import BotLogger

config = Config()
logger = BotLogger()
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

dp.message.middleware(BotLogger())


async def main() -> None:
    print("Bot started")
    logging.info("Bot started")
    setup(dp)
    logging.info("Set up handlers")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
