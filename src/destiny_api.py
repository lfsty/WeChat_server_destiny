from src.MY_CONST import *
from src.urlRequest import *
import asyncio
import json
from bs4 import BeautifulSoup
import re


def is_steamid64(input_text):
    """判断是否为steamid
    返回：True/False
    """
    if input_text.isdigit() and len(input_text) == 17 and input_text[:4] == '7656':
        return True
    else:
        return False


def is_bungie_membershipid(input_text):
    """判断是否为membershipID
    返回：True/False
    """
    if input_text.isdigit() and len(input_text) == 19 and input_text[:4] == '4611':
        return True
    else:
        return False


async def getXurLocation():
    """获取当时xur位置
    返回：若存在，则返回位置，若不存在则返回None，
            位置不在表中是情况返回“位置获取出错”，请及时更新json表
    """
    url = "https://xur.wiki"
    # data = urllib3.PoolManager().request(method='GET', url=url).data.decode()
    data = await GetResponseByUrl(url)
    soup = BeautifulSoup(data, 'html.parser')
    location_name_en = re.compile(r"\s").sub(
        '', soup.find(class_="location_name").get_text())
    if location_name_en == "XURHASDISSAPEARED":
        return None
    else:
        try:
            location = xur_location[location_name_en.lower()]
            return location
        except:
            return "位置获取出错"


async def getXurSaleItems():
    url = root + f"/Destiny2/Vendors/?components=402"
    data = await GetResponseByUrl(url)
    items = data["sales"]["data"]["2190858386"]["saleItems"]
    item_names = []
    for item in items:
        item_data = items[item]
        item_hash = item_data["itemHash"]
        item_name = ItemDefinition[str(item_hash)]["displayProperties"]["name"]
        item_names.append(item_name)
    return item_names[1:5]
