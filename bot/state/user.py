from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    wait_sum_to_up_balance = State()
    waiting_captcha = State()
