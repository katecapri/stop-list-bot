import json
import logging
import os.path
from asgiref.sync import async_to_sync
from uuid import uuid4

from src.integrations.iiko_integration import IikoIntegration
from src.celery_app import app as celery_app
import src.database.db_service as db_service


def create_dishes_file():
    try:
        dishes_from_base = async_to_sync(db_service.get_dishes_from_base)()
        dishes_dict = dict()
        for dish in dishes_from_base:
            dish_id = str(dish.iiko_id)
            if dish_id not in dishes_dict:
                dishes_dict[dish_id] = {
                    "sales_point_ids": [str(dish.sales_point_id)],
                    "code": dish.code,
                    "name": dish.name
                }
            else:
                dishes_dict[dish_id]["sales_point_ids"].append(str(dish.sales_point_id))
        with open('dishes_dict.json', 'w') as dict_file:
            dict_file.write(str(dishes_dict))
        return dishes_dict
    except Exception as e:
        logging.error(e, exc_info=True)


@celery_app.task(queue="stop_lists")
def save_stop_lists_for_restaurants_task():
    try:
        restaurants = async_to_sync(db_service.get_restaurants_from_base)()

        if not os.path.exists("dishes_dict.json"):
            dishes_dict = create_dishes_file()
        else:
            with open("dishes_dict.json") as dishes_file:
                dishes_dict = dishes_file.read()

        for restaurant in restaurants:
            save_stop_lists_for_restaurant_task.delay(str(restaurant.id), dishes_dict)
    except Exception as e:
        logging.error(e, exc_info=True)


@celery_app.task(queue="stop_lists")
def save_stop_lists_for_restaurant_task(restaurant_id, dishes_dict):
    try:
        unknown_sales_point_id = None
        stop_list = IikoIntegration().get_stop_list(restaurant_id)

        sales_points_in_base = async_to_sync(db_service.get_sales_points_from_base)()
        stop_lists_by_sales_point = dict()
        for sales_point in sales_points_in_base:
            stop_lists_by_sales_point[str(sales_point.id)] = list()
            if sales_point.name == "Unknown":
                unknown_sales_point_id = str(sales_point.id)

        for stop_product in stop_list:
            product_id = stop_product["productId"]
            if product_id in dishes_dict:
                sales_points = dishes_dict[product_id]["sales_point_ids"]
                for sales_point_id in sales_points:
                    stop_lists_by_sales_point[sales_point_id].append({
                        "product_id": product_id,
                        "code": dishes_dict[product_id]["code"],
                        "name": dishes_dict[product_id]["name"],
                    })
            else:
                stop_lists_by_sales_point[unknown_sales_point_id].append({
                        "product_id": product_id,
                        "code": "Unknown code",
                        "name": "Unknown name",
                    })

        for sales_point_id, stop_list in stop_lists_by_sales_point.items():
            stop_list_in_base = async_to_sync(db_service.get_stop_list_by_ids)(restaurant_id, sales_point_id)
            if stop_list_in_base:
                async_to_sync(db_service.update_stop_list)(stop_list_in_base.id, json.dumps(stop_list))
            else:
                async_to_sync(db_service.create_stop_list)(uuid4(), restaurant_id, sales_point_id, json.dumps(stop_list))
    except Exception as e:
        logging.error(e, exc_info=True)
