from aiogram.fsm.state import StatesGroup, State

class CreateUser(StatesGroup):
    input_username = State()


class DeleteUser(StatesGroup):
    input_username = State()


class CreateCoupon(StatesGroup):
    waiting_for_activation_limit = State()
    waiting_for_limit_per_user = State()
    waiting_for_amount = State()
    waiting_for_vip_flag = State()
    waiting_for_game = State()
    waiting_for_duration = State()
    waiting_for_expires = State()
