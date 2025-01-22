from dataclasses import dataclass

from aiogram.fsm.state import State, StatesGroup


@dataclass
class UserModel(StatesGroup):
    activity: State
    age: State
    city: State
    height: State
    weight: State
