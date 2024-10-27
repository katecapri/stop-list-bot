from aiogram import F, types, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum
import json
import logging

from src.tg_bot.filters.chat_types import ChatTypeFilter
from src.tg_bot.kbds.inline import get_callback_btns, get_restaurant_kb, get_sales_points_kb
from src.tg_bot.kbds.reply import get_keyboard

from src.database.repository import Repository
from src.database.db_service import get_stop_list_by_ids, get_answer_by_stop_list

logger = logging.getLogger('app')
user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


class EndOption(Enum):
    ACTUALIZE = 'Актуализировать'
    CHANGE_PLATFORM = 'Проверить по другой площадке'
    CHANGE_REST = 'Выбрать другой ресторан'

    @classmethod
    def get_values(cls):
        return [e.value for e in cls]


class AddProduct(StatesGroup):
    restaurant = State()
    sales_point = State()
    end_option_state = State()


class Verification(StatesGroup):
    phone = State()
    password = State()


# Выдача клавиатуры для выбора ресторана для получения стоп-листа
@user_private_router.message(F.text, StateFilter(None))
async def start_cmd(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        repository = Repository(session)
        chat_id = message.chat.id
        user = await repository.get_user_by_chat_id(chat_id)
        if not user:
            request_phone_kb = get_keyboard(['Поделиться телефоном'], placeholder="Предоставьте номер телефона",
                                            request_contact=1, sizes=(1, ))
            await message.reply("Предоставьте свой номер телефона", reply_markup=request_phone_kb)
            await state.set_state(Verification.phone)
        else:
            restaurants_for_user = await Repository(session).get_restaurants_for_user(user.id)
            number_of_2 = int(round(len(restaurants_for_user) / 2, 0))
            sizes = [2 for _ in range(number_of_2)]
            btns = {rest.short_name: f"get_rest_info_{rest.id}" for rest in restaurants_for_user}
            restaurant_kb = get_callback_btns(btns=btns, sizes=tuple(sizes))
            await message.answer("Выберите ресторан или введите название для поиска: ", reply_markup=restaurant_kb)
            await state.set_state(AddProduct.restaurant)
    except Exception as e:
        logger.error(e, exc_info=True)


@user_private_router.message(Verification.phone, F.contact)
async def ask_password(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        phone_number = message.contact.phone_number.replace('+', '')
        if phone_number.startswith('7'):
            phone_number = '8' + phone_number[1:]
        repository = Repository(session)
        user_with_phone = await repository.get_user_by_phone(phone_number)
        if not user_with_phone:
            await message.answer('Ваш телефон отсутствует в системе. Обратитесь к администратору.')
        else:
            await state.update_data(phone=phone_number)
            await message.answer('Введите пароль для доступа к сервису. '
                                 'Если у вас нет пароля, запросите его у администратора.',
                                 reply_markup=types.ReplyKeyboardRemove())
            await state.set_state(Verification.password)
    except Exception as e:
        logger.error(e, exc_info=True)


@user_private_router.message(Verification.password, F.text)
async def verify_password(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        password = message.text
        data = await state.get_data()
        phone = data["phone"]
        repository = Repository(session)
        correct_password = await repository.get_password_by_phone(phone)
        if correct_password != password:
            await message.answer('Пароль неверный. Введите пароль заново или обратитесь к администратору.')
        else:
            await message.answer('Вы успешно авторизованы.')
            chat_id = message.chat.id
            await repository.set_chat_id_for_phone(phone, chat_id)
            await state.clear()
    except Exception as e:
        logger.error(e, exc_info=True)


# После выбора ресторана пользователем выдача мест продаж для выбора
@user_private_router.callback_query(AddProduct.restaurant, F.data.startswith("get_rest_info_"))
async def get_sales_point_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        restaurant_id = callback.data.split("_")[-1]
        await state.update_data(restaurant=restaurant_id)
        all_sales_points = await Repository(session).get_sales_points()
        if all_sales_points:
            sales_point_kb = get_sales_points_kb(all_sales_points)
            await callback.message.answer("Выберите место продаж: ", reply_markup=sales_point_kb)
            await state.set_state(AddProduct.sales_point)
        else:
            await callback.message.answer("В базе отсутствуют места продаж, обратитесь к администратору.")
    except Exception as e:
        logger.error(e, exc_info=True)


# Если вместо выбора ресторана из списка пользователь ввел текст - предложение подходящих названий ресторанов
@user_private_router.message(AddProduct.restaurant, F.text)
async def get_rest_with_text(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        repository = Repository(session)
        chat_id = message.chat.id
        user = await repository.get_user_by_chat_id(chat_id)
        restaurants_for_user = await repository.get_restaurants_for_user_with_text(user.id, message.text)
        if not restaurants_for_user or message.text.lower() in ['all', 'все', 'всё']:
            restaurants_for_user = await repository.get_restaurants_for_user(user.id)
        if restaurants_for_user:
            number_of_2 = int(round(len(restaurants_for_user) / 2, 0))
            sizes = [2 for _ in range(number_of_2)]
            btns = {rest.short_name: f"get_rest_info_{rest.id}" for rest in restaurants_for_user}
            restaurant_kb = get_callback_btns(btns=btns, sizes=tuple(sizes))
            await message.answer("Выберите ресторан или введите название для поиска: ", reply_markup=restaurant_kb)
        else:
            await message.answer('Для вашего аккаунта не назначено ни одного ресторана. Обратитесь к администратору.',
                                 reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        logger.error(e, exc_info=True)


# Если вместо выбора ресторана из списка пользователь ввел текст - поиск подходящего названия ресторана
@user_private_router.callback_query(AddProduct.sales_point, F.data.startswith("get_stop_list_"))
async def get_stop_list(callback: types.CallbackQuery, state: FSMContext):
    try:
        sales_point_id = callback.data.split("_")[-1]
        await state.update_data(sales_point=sales_point_id)

        data = await state.get_data()
        await state.update_data(sales_point=sales_point_id)
        end_options_kb = get_keyboard(EndOption.get_values(), placeholder="Дальнейшее действие", sizes=(1, 1, 1))
        await state.set_state(AddProduct.end_option_state)

        stop_list_obj = await get_stop_list_by_ids(data["restaurant"], sales_point_id)
        if stop_list_obj:
            stop_list = await get_answer_by_stop_list(json.loads(stop_list_obj.stop_list))
            await callback.message.answer(stop_list)
            await callback.message.answer("Выберите дальнейшее действие", reply_markup=end_options_kb)
        else:
            await callback.message.answer("Ошибка при получении стоп-листа.")
            await callback.message.answer("Выберите дальнейшее действие", reply_markup=end_options_kb)
    except Exception as e:
        logger.error(e, exc_info=True)


@user_private_router.message(AddProduct.end_option_state)
async def give_action_after_end(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        if message.text not in EndOption.get_values():
            await message.answer(f"Выберите одно из доступных действий: {', '.join(EndOption.get_values())}.")
            return

        repository = Repository(session)
        if message.text == EndOption.ACTUALIZE.value:
            data = await state.get_data()
            stop_list_obj = await get_stop_list_by_ids(data["restaurant"], data["sales_point"])
            if stop_list_obj:
                stop_list = await get_answer_by_stop_list(json.loads(stop_list_obj.stop_list))
                await message.answer(stop_list)
            else:
                await message.answer("Ошибка при получении стоп-листа.")

        elif message.text == EndOption.CHANGE_REST.value:
            user = await repository.get_user_by_chat_id(message.chat.id)
            restaurants_for_user = await repository.get_restaurants_for_user(user.id)
            restaurant_kb = get_restaurant_kb(restaurants_for_user)
            await message.answer("Выберите ресторан или введите название для поиска: ", reply_markup=restaurant_kb)
            await state.set_state(AddProduct.restaurant)

        else:  # EndOption.CHANGE_PLATFORM
            all_sales_points = await repository.get_sales_points()
            sales_point_kb = get_sales_points_kb(all_sales_points)
            await message.answer("Выберите место продаж: ", reply_markup=sales_point_kb)
            await state.set_state(AddProduct.sales_point)
    except Exception as e:
        logger.error(e, exc_info=True)



