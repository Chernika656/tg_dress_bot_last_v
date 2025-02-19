from aiogram.fsm.state import StatesGroup, State

# class Gen(StatesGroup):
#     text_prompt = State()
#     img_prompt = State()

class ProfileStates(StatesGroup):
    height = State()
    weight = State()
    shoesize = State()

class Form(StatesGroup):
    wait_for_photo = State()
    wait_for_photo1 = State()
    update_menu = State()

