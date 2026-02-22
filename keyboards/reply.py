from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить задачу")],
        [KeyboardButton(text="📝 Задачи на сегодня")],
        [KeyboardButton(text="📚 Все задачи")],
        [KeyboardButton(text="⏰ Настроить дайджест")],
        [KeyboardButton(text="🌍 Таймзона")]
    ],
    resize_keyboard=True
)

date_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сегодня"), KeyboardButton(text="Завтра")],
        [KeyboardButton(text="Ввести дату вручную")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
