from aiogram import Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from user import UserModel

router = Router()
# database
user_database: dict[int, UserModel] = dict()  # type: ignore


def setup(dp: Dispatcher) -> None:
    dp.include_router(router)


@router.message(Command("start"))
async def start(message: Message) -> None:
    commands = [
        ("set_profile", "Установить параметры (рост, вес, ...)"),
        ("log_food", "Записать прием пищи"),
        ("log_water", "Записать выпитую воду"),
        ("log_workout", "Записать активность"),
        ("check_progress", "Показать текущий прогресс"),
    ]
    commands_msg = "\n".join(map(lambda p: f"/{p[0]}: {p[1]}", commands))
    await message.reply(commands_msg)
