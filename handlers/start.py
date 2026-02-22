from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from db import add_user
from keyboards.reply import main_kb

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    add_user(message.from_user.id)
    await message.answer(
        "👋 Привет!\nЯ помогу управлять задачами 📌",
        reply_markup=main_kb
    )
