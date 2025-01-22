import logging
from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


@dataclass(init=False)
class Config:
    BOT_TOKEN: str

    def __init__(self, dotenv_path: Path = Path(".env")) -> None:
        load_dotenv(dotenv_path)
        match getenv("BOT_TOKEN"):
            case None:
                raise KeyError("Config does not contain 'BOT_TOKEN' variable")
            case token:
                self.BOT_TOKEN = token
        logging.info(f"Read config: {self}")
