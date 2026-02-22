from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import datetime

from fsm.states import DigestFSM, TimezoneFSM
from keyboards.reply import main_kb
from db import set_digest_times, get_user_digest_times, get_user_timezone

router = Router()

@router.message(lambda m: m.text == "⏰ Настроить дайджест")
async def digest_start(message: Message, state: FSMContext):
    current = get_user_digest_times(message.from_user.id)
    await state.set_state(DigestFSM.times)
    await message.answer(
        "⏰ Введи время через запятую\n"
        "Пример: 07:00, 10:00, 14:00, 18:00\n\n"
        f"Текущие: {', '.join(current) if current else 'выключен'}"
    )

@router.message(DigestFSM.times)
async def digest_save(message: Message, state: FSMContext):
    # Кнопка «Таймзона» не должна парситься как время — переключаем на настройку таймзоны
    if message.text and message.text.strip() == "🌍 Таймзона":
        await state.clear()
        tz = get_user_timezone(message.from_user.id) or "Europe/Moscow"
        await state.set_state(TimezoneFSM.tz)
        await message.answer(
            f"🌍 Текущая: {tz}\nВведи новую таймзону (например Europe/Moscow, Asia/Tokyo)"
        )
        return

    raw = [t.strip() for t in message.text.split(",") if t.strip()]
    times = []
    for t in raw:
        try:
            datetime.strptime(t, "%H:%M")
            times.append(t)
        except ValueError:
            await message.answer(f"❗ Неверное время «{t}». Используйте формат ЧЧ:ММ (например 07:00, 14:30)")
            return
    if not times:
        await message.answer("❗ Введите хотя бы одно время в формате ЧЧ:ММ")
        return

    set_digest_times(message.from_user.id, times)
    await state.clear()
    await message.answer("✅ Дайджест сохранён", reply_markup=main_kb)
