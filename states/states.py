from aiogram.fsm.state import State, StatesGroup


class Reg(StatesGroup):
    goto_hub = State()

class Town(StatesGroup):
    street = State()
    sword_shop = State()
    ranger_shop = State()
    mage_shop = State()

class Outside(StatesGroup):
    crossroads = State()
    forest = State()
    field = State()