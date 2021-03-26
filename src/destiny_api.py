from src.MY_CONST import *
from src.urlRequest import *
import asyncio
import json
from bs4 import BeautifulSoup
import re
from collections import Counter
import urllib3


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
    try:
        data = await GetResponseByUrl(url)
        soup = BeautifulSoup(data, 'html.parser')
        location_name_en = re.compile(r"\s").sub(
            '', soup.find(class_="location_name").get_text())
    except:
        return "位置获取出错"
    if location_name_en == "XURHASDISSAPEARED":
        return "老九还没来"
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


async def getSteamIDByMembershipID(membershipid):
    try:
        url = f"https://www.bungie.net/en/Profile/{membershipid}"
        data = await GetResponseByUrl(url)
        soup = BeautifulSoup(data, 'html.parser')
        result = soup.find(
            class_='inner-text-content').find(class_='title').get_text()
        steamid_pattern = re.compile(r"7656[0-9]{13}")
        return steamid_pattern.search(result).group(0)
    except:
        print("getSteamIDByMembershipID出错")
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
            return "未查询到用户信息"
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
        return "查询出错，请稍后再试"


async def getPlayerdataBySteamID(steamid, UserName, season="13"):
    url = f"https://api.tracker.gg/api/v2/destiny-2/standard/profile/steam/{steamid}/segments/playlist?season={season}"
    try:
        response = await urllibRequestGet(url)
        data = json.loads(response)['data']
    except:
        return "elo数据获取出错"
    all_data = f"第{season}赛季:\n"
    for item in data:
        if item['metadata']['name'] in remain:
            tmp = "--------------\n"
            tmp += "模式："+remain[item['metadata']['name']]+"\n"
            tmp += "ELO："+str(item['stats']['elo']['value'])+"\n"
            tmp += "kd："+item['stats']['kd']['displayValue']+"\n"
            tmp += "kda："+item['stats']['kda']['displayValue']+"\n"
            all_data += tmp
        # tmp="分类："+item['attributes']['group']+"\n"
        # tmp+="模式名称："+item['metadata']['name']+"\n"
        # tmp+="世界排名："+str(item['stats']['elo']['rank'])+"\n"
        # tmp+="段位："+item['stats']['elo']['metadata']['rankName']+"\n"
        # tmp+="ELO："+str(item['stats']['elo']['value'])+"\n"
        # tmp+="世界排名百分比："+str(item['stats']['elo']['percentile'])+"\n"
        # tmp+="获胜次数："+str(item['stats']['activitiesWon']['value'])+"\n"
        # tmp+="百分比胜率："+item['stats']['wl']['displayValue']+"\n"
        # tmp+="kd："+item['stats']['kd']['displayValue']+"\n"
        # tmp+="kad："+item['stats']['kad']['displayValue']+"\n"
        # tmp+="kda："+item['stats']['kda']['displayValue']+"\n"
        # tmp+="助攻："+item['stats']['assists']['displayValue']+"\n"
        # tmp+="Kill per Game："+item['stats']['killsPga']['displayValue']+"\n\n"
        # all_data+=tmp
    return UserName + "\n" + all_data + "--------------"


async def getPartyMembersDataByMembershipID(destinyMembershipId, membershipType="3"):
    url = ROOT + \
        f"/Destiny2/{membershipType}/Profile/{destinyMembershipId}/?components=1000"
    resp = await GetResponseByUrl(url, need_header=True)
    resp = json.loads(resp)["Response"]
    if "data" in resp["profileTransitoryData"]:
        # 在线
        partyMembers_data = resp["profileTransitoryData"]["data"]["partyMembers"]
        partyMembers = []
        for item in partyMembers_data:
            tmp = {}
            tmp["membershipId"] = str(item["membershipId"])
            tmp["displayName"] = item["displayName"]
            partyMembers.append(tmp)
        return partyMembers
    else:
        # 不在线
        return None


async def getPartyMembersRaidReport(destinyMembershipId, membershipType="3"):
    partyMembers = await getPartyMembersDataByMembershipID(destinyMembershipId)
    if partyMembers == None:
        return "玩家不在线"
    else:
        resp_data = ""
        task_list = []
        for item in partyMembers:
            task_tmp = asyncio.create_task(getUserRaidReportByMemberShipID(
                item["membershipId"], item["displayName"], membershipType))
            task_list.append(task_tmp)
        for task_item in task_list:
            if resp_data != "":
                resp_data += "\n"
            resp_data += await task_item
        return resp_data


async def getPartyMembersElo(destinyMembershipId, membershipType="3"):
    partyMembers = await getPartyMembersDataByMembershipID(destinyMembershipId)
    if partyMembers == None:
        return "玩家不在线"
    else:
        resp_data = ""
        task_list = []
        for item in partyMembers:
            task_tmp = asyncio.create_task(getPlayerdataBySteamID(
                item["membershipId"], item["displayName"]))
            task_list.append(task_tmp)
        for task_item in task_list:
            if resp_data != "":
                resp_data += "\n"
            resp_data += await task_item
        return resp_data


async def SearchUsersByName(name, membershipType="-1"):
    url = ROOT + \
        f"/Destiny2/SearchDestinyPlayer/{membershipType}/{name}/"
    try:
        resp = await GetResponseByUrl(url, need_header=True)
        data = json.loads(resp)["Response"]
        if len(data) > 1:
            return None
        else:
            return data[0]["membershipId"]
    except:
        print("数据获取出错")
        return None
