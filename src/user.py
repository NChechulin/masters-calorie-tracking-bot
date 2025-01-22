from dataclasses import dataclass

from aiogram.fsm.state import State, StatesGroup


@dataclass
class User(StatesGroup):
    activity: State
    age: State
    city: State
    height: State
    weight: State
