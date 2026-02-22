from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from db import complete_task, delete_task, get_task_by_id
from fsm.states import EditTaskFSM

router = Router()


@router.callback_query(F.data.startswith("done:"))
async def done_task(cb: CallbackQuery):
    complete_task(cb.from_user.id, int(cb.data.split(":")[1]))
    await cb.message.edit_text("🎉 Задача выполнена")


@router.callback_query(F.data.startswith("delete:"))
async def delete_task_cb(cb: CallbackQuery):
    delete_task(cb.from_user.id, int(cb.data.split(":")[1]))
    await cb.message.edit_text("🗑 Задача удалена")


@router.callback_query(F.data.startswith("edit:"))
async def edit_task_start(cb: CallbackQuery, state: FSMContext):
    task_id = int(cb.data.split(":")[1])
    task = get_task_by_id(cb.from_user.id, task_id)
    if not task:
        await cb.answer("Задача не найдена", show_alert=True)
        return
    await state.set_state(EditTaskFSM.text)
    await state.update_data(edit_task_id=task_id)
    await cb.message.edit_text(f"✏️ Редактирование. Введите новый текст задачи (текущий: {task['text']})")
    await cb.answer()
