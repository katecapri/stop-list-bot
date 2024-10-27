from src.database.engine import session_maker
from src.database.repository import Repository


async def get_restaurants_from_base():
    async with session_maker() as session:
        repository = Repository(session)
        restaurants_from_base = await repository.get_restaurants()
    return restaurants_from_base


async def get_dishes_from_base():
    async with session_maker() as session:
        repository = Repository(session)
        dishes_from_base = await repository.get_dishes()
    return dishes_from_base


async def get_sales_points_from_base():
    async with session_maker() as session:
        repository = Repository(session)
        sales_points_from_base = await repository.get_sales_points()
    return sales_points_from_base


async def get_stop_list_by_ids(restaurant_id, sales_point_id):
    async with session_maker() as session:
        repository = Repository(session)
        stop_list = await repository.get_stop_list_by_ids(restaurant_id, sales_point_id)
    return stop_list


async def update_stop_list(stop_list_id, stop_list):
    async with session_maker() as session:
        repository = Repository(session)
        await repository.update_stop_list(stop_list_id, stop_list)


async def create_stop_list(id, restaurant_id, sales_point_id, stop_list):
    async with session_maker() as session:
        repository = Repository(session)
        await repository.create_stop_list(id, restaurant_id, sales_point_id, stop_list)


async def get_answer_by_stop_list(stop_list):
    if stop_list:
        result = ""
        if stop_list[0]["code"] == "Unknown code":
            for dish in stop_list:
                result += dish["product_id"] + "\n"
        else:
            for dish in stop_list:
                result += f'{dish["name"]} {dish["code"]}\n'
    else:
        result = "На данной площадке нет ни одного блюда в стоп-листе."
    return result
