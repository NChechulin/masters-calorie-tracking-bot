import logging

from aiogram import Dispatcher, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import Config
from user import UserModel, UserState

config = Config()
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


@router.message(Command("set_profile"))
async def set_profile(message: Message, state: FSMContext) -> None:
    await message.reply("Введи вес в кг:")
    await state.set_state(UserState.weight)


@router.message(UserState.weight)
async def read_weight(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(weight=float(message.text))  # type: ignore
        await message.reply("Введи рост в см:")
        await state.set_state(UserState.height)
    except ValueError as e:
        logging.error(f"Encountered an error while setting weight: {e}")
        await message.reply("Число должно быть float или int")


@router.message(UserState.height)
async def read_height(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(height=float(message.text))  # type: ignore
        await message.reply("Сколько тебе лет?")
        await state.set_state(UserState.age)
    except ValueError as e:
        logging.error(f"Encountered an error while setting height: {e}")
        await message.reply("Число должно быть float или int")


@router.message(UserState.age)
async def read_age(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(age=float(message.text))  # type: ignore
        await message.reply("Сколько минут активности у тебя в день?")
        await state.set_state(UserState.activity)
    except ValueError as e:
        logging.error(f"Encountered an error while setting age: {e}")
        await message.reply("Число должно быть float или int")


@router.message(UserState.activity)
async def read_activity(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(activity=float(message.text))  # type: ignore
        await message.reply("В каком городе ты находишься? (по-английски)")
        await state.set_state(UserState.city)
    except ValueError as e:
        logging.error(f"Encountered an error while setting activity: {e}")
        await message.reply("Число должно быть float или int")


@router.message(UserState.city)
async def read_city(message: Message, state: FSMContext) -> None:
    await state.update_data(city=message.text)

    user_data = await state.get_data()
    user_id = message.from_user.id  # type: ignore

    try:
        user = UserModel(**user_data)
        user_database[user_id] = user
        logging.info(f"Inserted new user: {user_database[user_id]}")
    except Exception as e:
        message.reply(f"Проиозшла ошибка: {e}")
        logging.error("Got an error while creating new user: {e}")

    await state.clear()
    await message.reply(
        f"Добавил тебя в базу! Вот твои цели на день:\n"
        f"Вода: {user.water_goal} мл\n"
        f"Калории: {user.calorie_goal} ккал."
    )
