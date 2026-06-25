from aiogram.fsm.state import StatesGroup, State

class Payments(StatesGroup):
    request_email = State()
