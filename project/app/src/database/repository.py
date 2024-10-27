from sqlalchemy import select, update

from src.database.models import User, Restaurant, UserRestaurant, Folder, SalesPoint, StopList, Dish


class Repository:
    def __init__(self, session):
        self.session = session
        self.model_user = User
        self.model_restaurant = Restaurant
        self.model_user_restaurant = UserRestaurant
        self.model_folder = Folder
        self.model_sales_point = SalesPoint
        self.model_stop_list = StopList
        self.model_dish = Dish

    async def get_user_by_phone(self, phone_number):
        query = select(self.model_user).where(self.model_user.phone_number == phone_number)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_user_by_chat_id(self, chat_id):
        query = select(self.model_user).where(self.model_user.chat_id == chat_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_password_by_phone(self, phone):
        query = select(self.model_user.password).where(self.model_user.phone_number == phone)
        result = await self.session.execute(query)
        return result.scalar()

    async def create_user(self, phone_number, first_name, last_name, password):
        new_user = self.model_user(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        self.session.add(new_user)
        await self.session.commit()
        return new_user.id

    async def set_chat_id_for_phone(self, phone, chat_id):
        query = update(self.model_user).where(self.model_user.phone_number == phone).values(chat_id=chat_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_restaurants(self):
        query = select(self.model_restaurant)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_restaurants_for_user(self, user_id):
        restaurants_query = select(self.model_user_restaurant.restaurant_id).\
            where(self.model_user_restaurant.user_id == user_id)
        restaurants_result = await self.session.execute(restaurants_query)
        restaurants_id = restaurants_result.scalars().all()
        query = select(self.model_restaurant).where(self.model_restaurant.id.in_(restaurants_id))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_restaurant_dy_id(self, restaurant_id):
        query = select(self.model_restaurant).where(self.model_restaurant.id == restaurant_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_restaurants_for_user_with_text(self, user_id, text):
        restaurants_query = select(self.model_user_restaurant.restaurant_id).\
            where(self.model_user_restaurant.user_id == user_id)
        restaurants_result = await self.session.execute(restaurants_query)
        restaurants_id = restaurants_result.scalars().all()
        text_filter = f"%{text}%"
        query = select(self.model_restaurant).where(
            (self.model_restaurant.name.ilike(text_filter)) | (self.model_restaurant.short_name.ilike(text_filter))
        ).where(self.model_restaurant.id.in_(restaurants_id))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_restaurant(self, rest_id, name, short_name):
        new_organization = self.model_restaurant(
            id=rest_id,
            name=name,
            short_name=short_name
        )
        self.session.add(new_organization)
        await self.session.commit()

    async def update_restaurant(self, rest_id, name, short_name):
        query = update(self.model_restaurant).where(self.model_restaurant.id == rest_id).values(
            name=name,
            short_name=short_name
        )
        await self.session.execute(query)
        await self.session.commit()

    async def create_user_restaurant(self, user_id, restaurant_id):
        new_user_restaurant = self.model_user_restaurant(
            user_id=user_id,
            restaurant_id=restaurant_id,
        )
        self.session.add(new_user_restaurant)
        await self.session.commit()

    async def get_folders(self):
        query = select(self.model_folder)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_folder(self, folder_id, name, parent_folder_id, top_folder_id):
        new_folder = self.model_folder(
            id=folder_id,
            name=name,
            parent_folder_id=parent_folder_id,
            top_folder_id=top_folder_id
        )
        self.session.add(new_folder)
        await self.session.commit()

    async def create_folders(self, folders):
        for folder in folders:
            self.session.add(folder)
        await self.session.commit()

    async def get_sales_points(self):
        query = select(self.model_sales_point)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_sales_points_by_folders(self):
        query = select(self.model_folder).where(self.model_folder.parent_folder_id == None)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_sales_point(self, id, folder_name, name, is_active=True):
        new_sales_point = self.model_sales_point(
            id=id,
            folder_name=folder_name,
            name=name,
            is_active=is_active
        )
        self.session.add(new_sales_point)
        await self.session.commit()

    async def get_dishes(self):
        query = select(self.model_dish)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_dishes(self, dishes):
        for dish in dishes:
            self.session.add(dish)
        await self.session.commit()

    async def get_stop_list_by_ids(self, restaurant_id, sales_point_id):
        query = select(self.model_stop_list).where(
            self.model_stop_list.restaurant_id == restaurant_id,
            self.model_stop_list.sales_point_id == sales_point_id
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def create_stop_list(self, id, restaurant_id, sales_point_id, stop_list):
        new_stop_list = self.model_stop_list(
            id=id,
            restaurant_id=restaurant_id,
            sales_point_id=sales_point_id,
            stop_list=stop_list
        )
        self.session.add(new_stop_list)
        await self.session.commit()

    async def update_stop_list(self, stop_list_id, stop_list):
        query = update(self.model_stop_list).where(
            self.model_stop_list.id == stop_list_id
        ).values(
            stop_list=stop_list
        )
        await self.session.execute(query)
        await self.session.commit()
