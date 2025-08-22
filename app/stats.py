from aiogram.fsm.state import StatesGroup, State

class Newsletter(StatesGroup):
    message = State()


class Newsonlyvip(StatesGroup):
    message = State()


class Newsonlybroke(StatesGroup):
    message = State()
