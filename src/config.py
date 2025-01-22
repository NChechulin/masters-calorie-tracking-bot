import logging
from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


@dataclass(init=False)
class Config:
    BOT_TOKEN: str
    WEATHER_TOKEN: str
    WEATHER_API_BASE: str
    FOOD_API_BASE: str

    def __init__(self, dotenv_path: Path = Path(".env")) -> None:
        load_dotenv(dotenv_path)
        match getenv("BOT_TOKEN"):
            case None:
                raise KeyError("Config does not contain 'BOT_TOKEN' variable")
            case token:
                self.BOT_TOKEN = token
        match getenv("WEATHER_TOKEN"):
            case None:
                raise KeyError("Config does not contain 'WEATHER_TOKEN' variable")
            case token:
                self.WEATHER_TOKEN = token
        match getenv("WEATHER_API_BASE"):
            case None:
                raise KeyError("Config does not contain 'WEATHER_API_BASE' variable")
            case url:
                self.WEATHER_API_BASE = url
        match getenv("FOOD_API_BASE"):
            case None:
                raise KeyError("Config does not contain 'FOOD_API_BASE' variable")
            case url:
                self.FOOD_API_BASE = url
        logging.info(f"Read config: {self}")
