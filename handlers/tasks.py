from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import timedelta, datetime
from pytz import timezone as pytz_timezone
from pytz import UnknownTimeZoneError

from fsm.states import AddTaskFSM, EditTaskFSM
from keyboards.reply import main_kb, date_kb
from keyboards.inline import task_inline_kb
from db import add_task, get_tasks, get_today_tasks_full, update_task, get_user_timezone

router = Router()

@router.message(lambda m: m.text == "➕ Добавить задачу")
async def add_task_start(message: Message, state: FSMContext):
    await state.set_state(AddTaskFSM.text)
    await message.answer("✍️ Введи текст задачи")

@router.message(AddTaskFSM.text)
async def add_task_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(AddTaskFSM.date)
    await message.answer("📅 Выбери дату", reply_markup=date_kb)

def _user_today(user_id: int):
    """Дата «сегодня» в таймзоне пользователя."""
    tz_name = get_user_timezone(user_id) or "Europe/Moscow"
    try:
        tz = pytz_timezone(tz_name)
    except UnknownTimeZoneError:
        tz = pytz_timezone("Europe/Moscow")
    return datetime.now(tz).date()


@router.message(AddTaskFSM.date)
async def add_task_date(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "Сегодня":
        task_date = _user_today(user_id)
    elif message.text == "Завтра":
        task_date = _user_today(user_id) + timedelta(days=1)
    elif message.text == "Ввести дату вручную":
        await message.answer("📅 Введите дату в формате ГГГГ-ММ-ДД (например 2025-12-31)")
        return
    else:
        try:
            task_date = datetime.strptime(message.text.strip(), "%Y-%m-%d").date()
        except ValueError:
            await message.answer("❗ Неверный формат. Используйте ГГГГ-ММ-ДД (например 2025-12-31)")
            return

    await state.update_data(task_date=task_date.isoformat())
    await state.set_state(AddTaskFSM.time)
    await message.answer("⏰ Введи время в формате ЧЧ:ММ (например 14:30)")

@router.message(AddTaskFSM.time)
async def add_task_time(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text.strip(), "%H:%M")
    except (ValueError, AttributeError):
        await message.answer("❗ Введите время в формате ЧЧ:ММ (например 14:30)")
        return
    data = await state.get_data()

    add_task(
        message.from_user.id,
        data["text"],
        data["task_date"],
        message.text.strip()
    )

    await state.clear()
    await message.answer("✅ Задача добавлена", reply_markup=main_kb)

# --- Редактирование задачи (EditTaskFSM) ---

@router.message(EditTaskFSM.text)
async def edit_task_text(message: Message, state: FSMContext):
    await state.update_data(edit_text=message.text)
    await state.set_state(EditTaskFSM.date)
    await message.answer("📅 Выбери новую дату", reply_markup=date_kb)


@router.message(EditTaskFSM.date)
async def edit_task_date(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "Сегодня":
        task_date = _user_today(user_id)
    elif message.text == "Завтра":
        task_date = _user_today(user_id) + timedelta(days=1)
    elif message.text == "Ввести дату вручную":
        await message.answer("📅 Введите дату в формате ГГГГ-ММ-ДД (например 2025-12-31)")
        return
    else:
        try:
            task_date = datetime.strptime(message.text.strip(), "%Y-%m-%d").date()
        except ValueError:
            await message.answer("❗ Неверный формат. Используйте ГГГГ-ММ-ДД (например 2025-12-31)")
            return
    await state.update_data(edit_task_date=task_date.isoformat())
    await state.set_state(EditTaskFSM.time)
    await message.answer("⏰ Введи новое время в формате ЧЧ:ММ (например 14:30)")


@router.message(EditTaskFSM.time)
async def edit_task_time(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text.strip(), "%H:%M")
    except (ValueError, AttributeError):
        await message.answer("❗ Введите время в формате ЧЧ:ММ (например 14:30)")
        return
    data = await state.get_data()
    task_id = data["edit_task_id"]
    update_task(
        message.from_user.id,
        task_id,
        data["edit_text"],
        data["edit_task_date"],
        message.text.strip()
    )
    await state.clear()
    await message.answer("✅ Задача обновлена", reply_markup=main_kb)


# --- Просмотр задач ---

@router.message(lambda m: m.text == "📝 Задачи на сегодня")
async def today_tasks(message: Message):
    user_id = message.from_user.id
    today_iso = _user_today(user_id).isoformat()
    tasks = get_today_tasks_full(user_id, today_iso)
    if not tasks:
        await message.answer("📭 Сегодня задач нет")
        return

    for t in tasks:
        done = bool(t["completed"])
        prefix = "✅ Выполнена: " if done else ""
        await message.answer(
            f"{prefix}{t['text']} ⏰ {t['remind_time']}",
            reply_markup=task_inline_kb(t["id"], completed=done)
        )


@router.message(lambda m: m.text == "📚 Все задачи")
async def all_tasks(message: Message):
    tasks = get_tasks(message.from_user.id)
    if not tasks:
        await message.answer("📭 Задач нет")
        return

    for t in tasks:
        done = bool(t["completed"])
        prefix = "✅ Выполнена: " if done else ""
        await message.answer(
            f"{prefix}{t['text']} ({t['task_date']} ⏰ {t['remind_time']})",
            reply_markup=task_inline_kb(t["id"], completed=done)
        )
