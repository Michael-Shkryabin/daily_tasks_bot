from aiogram.fsm.state import StatesGroup, State

class AddTaskFSM(StatesGroup):
    text = State()
    date = State()
    time = State()

class EditTaskFSM(StatesGroup):
    text = State()
    date = State()
    time = State()

class DigestFSM(StatesGroup):
    times = State()

class TimezoneFSM(StatesGroup):
    tz = State()
