import json
import os
from uuid import uuid4
from src.integrations.iiko_integration import IikoIntegration
from src.database.engine import session_maker
from src.database.repository import Repository
from src.services.iiko_service import get_folders_from_iiko_groups, get_dishes_from_iiko_menu
from src.tasks import save_stop_lists_for_restaurants_task


async def get_restaurant_short_name_by_name(restaurant_name):
    try:
        restaurant_main_words = restaurant_name.split(' ')[1:-1]
        short_name = " ".join(restaurant_main_words) if restaurant_main_words else restaurant_name
    except:
        short_name = restaurant_name
    return short_name


async def fill_organizations_on_start():
    async with session_maker() as session:
        repository = Repository(session)
        organizations_in_base = await repository.get_restaurants()
        if not organizations_in_base:
            iiko_organizations = await IikoIntegration().get_restaurants()
            for restaurant in iiko_organizations:
                restaurant_id = restaurant['id']
                restaurant_name = restaurant['name']
                existence_restaurant = await repository.get_restaurant_dy_id(restaurant_id)
                if not existence_restaurant:
                    short_name = await get_restaurant_short_name_by_name(restaurant_name)
                    await repository.create_restaurant(restaurant_id, restaurant_name, short_name)
                else:
                    if existence_restaurant.name != restaurant_name:
                        await repository.update_restaurant(restaurant_id, restaurant_name,
                                                           existence_restaurant.short_name)


async def fill_folders_on_start():
    async with session_maker() as session:
        repository = Repository(session)
        folders_in_base = await repository.get_folders()
        if not folders_in_base:
            menu_from_iiko = await IikoIntegration().get_menu()
            folders_to_save, top_folders_dict = await get_folders_from_iiko_groups(menu_from_iiko["groups"])
            await repository.create_folders(folders_to_save)
            unknown_folder_id = uuid4()
            await repository.create_folder(unknown_folder_id, "Unknown", None, unknown_folder_id)

            top_folders = await repository.get_sales_points_by_folders()
            for top_folder in top_folders:
                await repository.create_sales_point(top_folder.id, top_folder.name, top_folder.name)

            dishes_to_save = await get_dishes_from_iiko_menu(menu_from_iiko, top_folders_dict)
            await repository.create_dishes(dishes_to_save)


async def fill_sales_points_on_start():
    async with session_maker() as session:
        repository = Repository(session)
        sales_points_in_base = await repository.get_sales_points()
        if not sales_points_in_base:
            top_folders = await repository.get_sales_points_by_folders()
            for top_folder in top_folders:
                await repository.create_sales_point(top_folder.id, top_folder.name, top_folder.name)
            await repository.create_sales_point(uuid4(), "Unknown", "Отсутствует во внешнем меню", is_active=True)


async def fill_menu_on_start():
    async with session_maker() as session:
        repository = Repository(session)
        dishes_in_base = await repository.get_dishes()
        if not dishes_in_base:
            menu_from_iiko = await IikoIntegration().get_menu()
            dishes_to_save = await get_dishes_from_iiko_menu(menu_from_iiko)
            await repository.create_dishes(dishes_to_save)


async def fill_users_on_start():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(parent_dir + "/users_data.json") as users_file:
        users = json.loads(users_file.read())
    async with session_maker() as session:
        repository = Repository(session)
        for user in users:
            user_in_base = await repository.get_user_by_phone(user['phone_number'])
            if not user_in_base:
                user_id = await repository.create_user(
                    user['phone_number'], user['first_name'], user['last_name'], user['password']
                )
                restaurants = await repository.get_restaurants()
                for restaurant in restaurants:
                    await repository.create_user_restaurant(user_id, restaurant.id)


async def fill_db_on_start():
    await fill_organizations_on_start()
    await fill_folders_on_start()
    await fill_sales_points_on_start()
    await fill_menu_on_start()
    await fill_users_on_start()
    save_stop_lists_for_restaurants_task.delay()
