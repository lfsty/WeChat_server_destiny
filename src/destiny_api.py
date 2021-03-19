from src.MY_CONST import *
from src.urlRequest import *
import asyncio
import json
from bs4 import BeautifulSoup
import re
from collections import Counter


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
    url = ROOT + f"/Destiny2/Vendors/?components=402"
    data = await GetResponseByUrl(url, need_header=True)
    data = json.loads(data)["Response"]
    items = data["sales"]["data"]["2190858386"]["saleItems"]
    item_names = []
    for item in items:
        item_data = items[item]
        item_hash = item_data["itemHash"]
        item_name = ItemDefinition[str(item_hash)]["displayProperties"]["name"]
        item_names.append(item_name)
    return item_names[1:5]


async def getCharacterIdsByMembershipId(destinyMembershipId, membershipType="3"):
    try:
        characterIds = []
        url = ROOT + \
            f"/Destiny2/{membershipType}/Account/{destinyMembershipId}/Stats/?groups=General"
        resp = await GetResponseByUrl(url, need_header=True)
        resp = json.loads(resp)["Response"]
        for item in resp["characters"]:
            characterIds.append(item["characterId"])
        return characterIds
    except:
        print("getCharacterIdsByMembershipId出错")
        return None


async def getMembershipIDBySteamID(steamid):
    try:
        url = ROOT + \
            f"/User/GetMembershipFromHardLinkedCredential/SteamId/{steamid}/"
        resp = await GetResponseByUrl(url, need_header=True)
        resp = json.loads(resp)["Response"]
        return resp['membershipId']
    except:
        print("getMembershipIDBySteamID出错")
        return None


async def getSteamIDByMembership(membershipid):
    try:
        url = f"https://www.bungie.net/en/Profile/{membershipid}"
        data = GetResponseByUrl(url)
        soup = BeautifulSoup(data, 'html.parser')
        result = soup.find(
            class_='inner-text-content').find(class_='title').get_text()
        steamid_pattern = re.compile(r"7656[0-9]{13}")
        return steamid_pattern.search(result).group(0)
    except:
        print("getSteamIDByMembership出错")
        return None


async def getUsernameByMenbershipid(menbershipid):
    try:
        url = ROOT + f"/User/GetMembershipsById/{menbershipid}/-1/"
        resp = await GetResponseByUrl(url, need_header=True)
        resp = json.loads(resp)["Response"]
        return resp['destinyMemberships'][0]['LastSeenDisplayName']
    except:
        print("getUsernameByMenbershipid出错")
        return None


async def getUserRaidReportByCharacterID(characterID, destinyMembershipId, membershipType="3"):
    url = ROOT + \
        f"/Destiny2/{membershipType}/Account/{destinyMembershipId}/Character/{characterID}/Stats/Activities/?count=250&mode=raid&page=0"
    try:
        resp = await GetResponseByUrl(url, need_header=True)
    except:
        print("获取用户信息失败")
        return None
    resp = json.loads(resp)["Response"]
    raid_data = {}
    if resp != {}:
        try:
            for item in resp["activities"]:
                if item['values']['completed']['basic']['displayValue'] == "Yes":
                    activityid = str(item["activityDetails"]["referenceId"])
                    name = ActivityDefinition[activityid]["displayProperties"]["name"]
                    if name in raid_data:
                        raid_data[name] += 1
                    else:
                        raid_data[name] = 1
        except:
            print("读取用户信息失败")
            return None
        return raid_data
    else:
        return None


async def getUserRaidReportByMemberShipID(destinyMembershipId, UserName, membershipType="3"):
    try:
        tasks = []
        raid_data = {}
        characterIds = await getCharacterIdsByMembershipId(destinyMembershipId)
        if characterIds == None:
            return None
        for characterID in characterIds:
            task_tmp = asyncio.create_task(getUserRaidReportByCharacterID(
                characterID, destinyMembershipId, membershipType))
            tasks.append(task_tmp)
        for task in tasks:
            data = await task
            raid_data = dict(Counter(raid_data)+Counter(data))
        resp_data = "------------------\n"
        for item in raid_data:
            resp_data += item + "："+str(raid_data[item])+"次\n"
        resp_data += "------------------"
        return UserName + "\nRaid通关次数：\n"+resp_data
    except:
        return None
