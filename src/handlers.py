import logging

import requests
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
    user_id = message.from_user.id  # type: ignore  # type: ignore

    try:
        user = UserModel(**user_data)
        user_database[user_id] = user
        logging.info(f"Inserted new user: {user_database[user_id]}")

        await state.clear()
        await message.reply(
            f"Добавил тебя в базу! Вот твои цели на день:\n"
            f"Вода: {user.water_goal} мл\n"
            f"Калории: {user.calorie_goal} ккал."
        )
    except Exception as e:
        await message.reply(f"Проиозшла ошибка: {e}")
        logging.error(f"Got an error while creating new user: {e}")


async def check_user_in_db(message: Message) -> bool:
    user_id = message.from_user.id  # type: ignore
    if user_id not in user_database:
        await message.reply("Тебя нет в базе. Вызови /set_profile")
        return False
    return True


@router.message(Command("log_water"))
async def log_water(message: Message) -> None:
    try:
        if not await check_user_in_db(message):
            return
        user_id = message.from_user.id  # type: ignore

        raw_data = message.text.split()  # type: ignore

        if len(raw_data) < 2:
            await message.reply("Ошибка. Пример: /log_water 250")
            return

        water_consumed = int(raw_data[1])

        user_database[user_id].logged_water += water_consumed
        remained_water = (
            user_database[user_id].water_goal - user_database[user_id].logged_water
        )

        await message.reply(f"Осталось выпить еще {max(0, remained_water)} мл")

    except ValueError:
        await message.reply("Число должно быть float или int")


async def process_food(message: Message, user_id: int, calories_100g: float) -> None:
    try:
        quantity = float(message.text)  # type: ignore
        total_calories = float((quantity / 100) * calories_100g)

        user_database[user_id].logged_calories += total_calories
        await message.reply(f"Учел {total_calories} ккал")
    except ValueError:
        await message.reply("Вес должен быть в граммах")


def get_calories_in_food(food_name: str) -> float:
    response = requests.get(
        config.FOOD_API_BASE,
        params={  # type: ignore
            "action": "process",
            "search_terms": food_name,
            "json": True,
        },
        timeout=5,
    )

    if response.status_code != 200:
        raise Exception(
            f"Got an error while getting data for {food_name}: {response.text}"
        )

    data = response.json()
    products = data.get("products", [])
    if not products:
        raise Exception("FOOD API did not return any products matching the search term")

    product = products[0]
    calories_per_100g = product.get("nutriments", {}).get("energy-kcal_100g", 0)

    if not calories_per_100g:
        raise Exception(f"Could not get nutrients for {food_name}")

    return float(calories_per_100g)


@router.message(Command("log_food"))
async def log_food(message: Message) -> None:
    try:
        user_id = message.from_user.id  # type: ignore

        if not await check_user_in_db(message):
            return

        raw_data = message.text.split()  # type: ignore

        if len(raw_data) < 2:
            await message.reply("Введи что ты ел, пожалуйста")
            return

        food_name = raw_data[1]
        calories_per_100g = get_calories_in_food(food_name)

        await message.reply(
            f"Калорийность {food_name}: {calories_per_100g} ккал на 100г."
            "Сколько г ты съел(а)?"
        )

        @router.message()
        async def handle_eaten_food(message: Message) -> None:
            await process_food(message, user_id, calories_per_100g)

    except Exception as e:
        msg = f"Got an error: {e}"
        logging.error(msg)
        await message.reply(msg)


@router.message(Command("log_workout"))
async def log_workout(message: Message) -> None:
    try:
        user_id = message.from_user.id  # type: ignore

        if not await check_user_in_db(message):
            return

        raw_data = message.text.split()  # type: ignore

        if len(raw_data) < 3:
            await message.reply("Ошибка: /log_workout <тип тренировки> <время (мин)>")
            return

        name = raw_data[1]
        workout_duration = int(raw_data[2])

        burnt_calories = workout_duration * 10
        drunk_water = int((workout_duration / 30) * 200)

        user_database[user_id].burnt_calories += burnt_calories
        user_database[user_id].logged_water += drunk_water

        await message.reply(
            f"{name} {workout_duration} минут — {burnt_calories} ккал."
            + f"Не забудь выпить {drunk_water} мл воды."
        )

    except Exception as e:
        msg = f"Got an error: {e}"
        logging.error(msg)
        await message.reply(msg)


@router.message(Command("check_progress"))
async def check_progress(message: Message) -> None:
    try:
        user_id = message.from_user.id  # type: ignore

        if not await check_user_in_db(message):
            return

        user = user_database[user_id]
        await message.reply(user.progress_msg())

    except Exception as e:
        msg = f"Got an error: {e}"
        logging.error(msg)
        await message.reply(msg)
