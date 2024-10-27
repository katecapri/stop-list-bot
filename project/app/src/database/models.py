from datetime import datetime
from uuid import uuid4
from sqlalchemy import MetaData, Column, String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base(metadata=MetaData())


class User(Base):
    __tablename__ = 'users'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4())
    phone_number = Column(String(), nullable=False)
    chat_id = Column(Integer())
    first_name = Column(String(), nullable=False)
    last_name = Column(String(), nullable=False)
    password = Column(String(), nullable=False)

    user_restaurants = relationship('UserRestaurant', cascade='all, delete')


class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    name = Column(String(), nullable=False)
    short_name = Column(String(), nullable=False)

    stop_lists = relationship('StopList', cascade='all, delete')
    user_restaurants = relationship('UserRestaurant', cascade='all, delete')


class UserRestaurant(Base):
    __tablename__ = 'users_restaurants'

    user_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE"), primary_key=True)
    restaurant_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(Restaurant.id, ondelete="CASCADE"),
                           primary_key=True)

    user = relationship(User, back_populates='user_restaurants')
    restaurant = relationship(Restaurant, back_populates='user_restaurants')


class Folder(Base):
    __tablename__ = 'folders'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    name = Column(String(), nullable=False)
    parent_folder_id = Column(postgresql.UUID(as_uuid=True))
    top_folder_id = Column(postgresql.UUID(as_uuid=True), nullable=False)

    sales_point = relationship('SalesPoint', cascade='all, delete')


class SalesPoint(Base):
    __tablename__ = 'sales_points'

    id = Column(postgresql.UUID(as_uuid=True), ForeignKey(Folder.id, ondelete="CASCADE"), primary_key=True)
    folder_name = Column(String(), nullable=False)
    name = Column(String(), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    folder = relationship(Folder, back_populates='sales_point')
    stop_lists = relationship('StopList', cascade='all, delete')


class StopList(Base):
    __tablename__ = 'stop_lists'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4())
    restaurant_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(Restaurant.id, ondelete="CASCADE"))
    sales_point_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(SalesPoint.id, ondelete="CASCADE"))
    stop_list = Column(Text())
    created = Column(DateTime(), default=datetime.now(), onupdate=datetime.now())

    restaurant = relationship(Restaurant, back_populates='stop_lists')
    sales_point = relationship(SalesPoint, back_populates='stop_lists')


class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4())
    iiko_id = Column(postgresql.UUID(as_uuid=True))
    group_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(Folder.id, ondelete="CASCADE"))
    sales_point_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(SalesPoint.id, ondelete="CASCADE"), nullable=True)
    code = Column(String(), nullable=False)
    name = Column(String(), nullable=False)
