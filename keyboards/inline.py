from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def task_inline_kb(task_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="✏️", callback_data=f"edit:{task_id}"),
            InlineKeyboardButton(text="✅", callback_data=f"done:{task_id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"delete:{task_id}")
        ]]
    )
