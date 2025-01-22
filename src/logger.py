from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message


class BotLogger(BaseMiddleware):
    async def __call__(  # type: ignore[override]
        self,
        handler: Callable,
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        print(f"Received a message:\t{event.text}")
        return await handler(event, data)
