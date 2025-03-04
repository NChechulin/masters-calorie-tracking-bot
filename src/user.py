from dataclasses import dataclass

import requests
from aiogram.fsm.state import State, StatesGroup

from config import Config

config = Config()


class UserState(StatesGroup):
    activity: State = State()
    age: State = State()
    city: State = State()
    height: State = State()
    weight: State = State()


@dataclass
class UserModel:
    activity: float
    age: float
    city: str
    height: float
    weight: float
    water_goal: int = 0
    calorie_goal: int = 0
    logged_water: float = 0
    logged_calories: float = 0
    burnt_calories: float = 0

    def get_temperature(self) -> float:
        response = requests.get(
            config.WEATHER_API_BASE,
            params={
                "q": self.city,
                "appid": config.WEATHER_TOKEN,
                "units": "metric",
            },
            timeout=5,
        )

        if response.status_code == 200:
            temp = float(response.json()["main"]["temp"])
            return temp
        else:
            raise ValueError(
                f"Incorrect city might have been entered. API response: {response}"
            )

    def __post_init__(self) -> None:
        # data validation
        if self.activity < 0 or self.activity >= 24 * 60:
            raise ValueError("Activity can not be < 0 or > 24 hrs")
        if self.age <= 0:
            raise ValueError("Age can not be negative")
        if self.height <= 0:
            raise ValueError("Height can not be negative")
        if self.weight <= 0:
            raise ValueError("Weight can not be negative")

        # requirements calculation
        self.water_goal = int(self.weight * 30 + 500 * (self.activity / 30))
        temp = self.get_temperature()
        if temp > 25:
            self.water_goal += 500

        self.calorie_goal = int(10 * self.weight + 6.25 * self.height - 5 * self.age)
        if self.activity > 50:
            self.calorie_goal += 300

    def progress_msg(self) -> str:
        water_left = max(0, self.water_goal - self.logged_water)
        balance = int(self.logged_calories - self.burnt_calories)
        cl = self.logged_calories
        cg = self.calorie_goal
        lines = [
            "Твой прогресс:",
            f"Вода: {self.logged_water} / {self.water_goal} мл (еще {water_left} мл)",
            f"Калории: {cl} / {cg} ккал (баланс {balance} ккал)",
        ]
        return "\n".join(lines)
