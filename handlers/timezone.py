from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from pytz import timezone as pytz_timezone
from pytz import UnknownTimeZoneError

from fsm.states import TimezoneFSM
from keyboards.reply import main_kb
from db import set_user_timezone, get_user_timezone

router = Router()


@router.message(lambda m: m.text == "🌍 Таймзона")
async def tz_start(message: Message, state: FSMContext):
    tz = get_user_timezone(message.from_user.id) or "Europe/Moscow"
    await state.set_state(TimezoneFSM.tz)
    await message.answer(
        f"🌍 Текущая: {tz}\nВведи новую таймзону (например Europe/Moscow, Asia/Tokyo)"
    )


@router.message(TimezoneFSM.tz)
async def tz_save(message: Message, state: FSMContext):
    tz_name = message.text.strip()
    try:
        pytz_timezone(tz_name)
    except UnknownTimeZoneError:
        await message.answer(
            f"❗ Неизвестная таймзона «{tz_name}». "
            "Примеры: Europe/Moscow, Europe/London, Asia/Tokyo"
        )
        return
    set_user_timezone(message.from_user.id, tz_name)
    await state.clear()
    await message.answer("✅ Таймзона сохранена", reply_markup=main_kb)
