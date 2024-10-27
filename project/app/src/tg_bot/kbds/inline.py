from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_callback_btns(*, btns, sizes):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()


def get_restaurant_kb(restaurants):
    number_of_2 = int(round(len(restaurants) / 2, 0))
    sizes = [2 for _ in range(number_of_2)]
    btns = {rest.short_name: f"get_rest_info_{rest.id}" for rest in restaurants}
    return get_callback_btns(btns=btns, sizes=tuple(sizes))


def get_sales_points_kb(sales_points):
    sizes = [1 for _ in range(len(sales_points))]
    btns = {sales_point.name: f"get_stop_list_{sales_point.id}" for sales_point in sales_points}
    return get_callback_btns(btns=btns, sizes=tuple(sizes))
