import aiofiles
from uuid import uuid4

from src.database.models import Folder, Dish


def get_top_folders_id_dict_for_groups(iiko_groups):
    top_folders_dict = dict()
    groups_for_search = list()
    for iiko_group in iiko_groups:
        if iiko_group["isGroupModifier"]:
            continue
        if not iiko_group['parentGroup']:
            top_folders_dict[iiko_group['id']] = iiko_group['id']
        else:
            if iiko_group['parentGroup'] in top_folders_dict:
                top_folders_dict[iiko_group['id']] = top_folders_dict[iiko_group['parentGroup']]
            else:
                groups_for_search.append(iiko_group)

    while groups_for_search:
        new_groups_for_search = list()
        for iiko_group in groups_for_search:
            if iiko_group['parentGroup'] in top_folders_dict:
                top_folders_dict[iiko_group['id']] = top_folders_dict[iiko_group['parentGroup']]
            else:
                new_groups_for_search.append(iiko_group)
        groups_for_search = new_groups_for_search
    return top_folders_dict


async def get_folders_from_iiko_groups(iiko_groups):
    top_folders_dict = get_top_folders_id_dict_for_groups(iiko_groups)
    new_folders = list()
    for iiko_group in iiko_groups:
        if not iiko_group["isGroupModifier"]:
            new_folder = Folder(
                id=iiko_group['id'],
                name=iiko_group['name'],
                parent_folder_id=iiko_group['parentGroup'],
                top_folder_id=top_folders_dict[iiko_group['id']],
            )
            new_folders.append(new_folder)
    return new_folders, top_folders_dict


async def get_dishes_from_iiko_menu(iiko_menu, top_folders_dict=None):
    if not top_folders_dict:
        top_folders_dict = get_top_folders_id_dict_for_groups(iiko_menu["groups"])
    new_dishes = list()
    dishes_dict = dict()
    for product in iiko_menu["products"]:
        if product["type"] == "Dish":
            sales_point_id = top_folders_dict[product['parentGroup']] \
                if product['parentGroup'] in top_folders_dict else None
            new_dish = Dish(
                id=uuid4(),
                iiko_id=product['id'],
                group_id=product['parentGroup'],
                sales_point_id=sales_point_id,
                code=product['code'],
                name=product['name'],
            )
            new_dishes.append(new_dish)
            if product['id'] not in dishes_dict:
                dishes_dict[product['id']] = {
                    "sales_point_ids": [str(sales_point_id)],
                    "code": product['code'],
                    "name": product['name']
                }
            else:
                dishes_dict[product['id']]["sales_point_ids"].append(sales_point_id)

    async with aiofiles.open('dishes_dict.json', 'w') as dishes_file:
        await dishes_file.write(str(dishes_file))

    return new_dishes
