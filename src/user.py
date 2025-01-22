from dataclasses import dataclass

from aiogram.fsm.state import State, StatesGroup


@dataclass
class UserState(StatesGroup):
    activity: State
    age: State
    city: State
    height: State
    weight: State


@dataclass
class UserModel:
    activity: float
    age: float
    city: str
    height: float
    weight: float
    water_goal: float = 0
    calorie_goal: float = 0
    logged_water: float = 0
    logged_calories: float = 0
    burnt_calories: float = 0

    def __post_init__(self) -> None:
        if self.activity < 0 or self.activity >= 24 * 60:
            raise ValueError("Activity can not be < 0 or > 24 hrs")
        if self.age <= 0:
            raise ValueError("Age can not be negative")
        if self.height <= 0:
            raise ValueError("Height can not be negative")
        if self.weight <= 0:
            raise ValueError("Weight can not be negative")
