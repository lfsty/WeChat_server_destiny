from src.MY_CONST import *
from src.urlRequest import *
import asyncio
import json
from bs4 import BeautifulSoup
import re
from collections import Counter
import urllib3


# 读取Bungie的Manifest文件
with open("./Manifest/DestinyInventoryItemDefinition.json", "r") as f:
    ItemDefinition = json.load(f)

with open("./Manifest/DestinyActivityDefinition.json", "r") as f:
    ActivityDefinition = json.load(f)


def is_steamid64(input_text):
    """
    判断是否为SteamID

    Args:
        input_text:需要判断的文本
    Returns:
        True/False
    """
    if input_text.isdigit() and len(input_text) == 17 and input_text[:4] == '7656':
        return True
    else:
        return False


def is_bungie_membershipid(input_text):
    """
    判断是否为MembershipID

    Args:
        input_text:需要判断的文本
    Returns:
        True/False
    """
    if input_text.isdigit() and len(input_text) == 19 and input_text[:4] == '4611':
        return True
    else:
        return False


async def getXurLocation():
    """
    获取当时xur位置

    Args:
        None
    Returns:
        若存在，则返回位置，若不存在则返回None，
        位置不在表中是情况返回“XUR位置转化出错”，请及时更新json表
    """
    url = "https://xur.wiki"
    try:
        data = await GetResponseByUrl(url)
        soup = BeautifulSoup(data, 'html.parser')
        location_name_en = re.compile(r"\s").sub(
            '', soup.find(class_="location_name").get_text())
    except:
        ACCESS.debug("云获取XUR位置出错")
        return "位置获取出错"
    if location_name_en == "XURHASDISSAPEARED":
        return "老九还没来"
    else:
        try:
            location = xur_location[location_name_en.lower()]
            return location
        except:
            ACCESS.debug("XUR位置转换出错")
            return "位置获取出错"


async def getXurSaleItems():
    """
    获取XUR所售卖的信息

    Args:
        None
    Returns:
        售卖信息的list
    """
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
    """
    通过MembershipID获取用户的CharacterID

    Args:
        destinyMembershipId:命运2的MembershipID
        membershipType:用户类型，默认为3（steam平台）
    Returns:
        characterIDs列表
    """
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
        ACCESS.debug("getCharacterIdsByMembershipId出错")
        return None


async def getMembershipIDBySteamID(steamid):
    """
    通过SteamID获取用户MembershiID

    Args:
        Steamid
    Returns:
        MembershipID
    """
    try:
        url = ROOT + \
            f"/User/GetMembershipFromHardLinkedCredential/SteamId/{steamid}/"
        resp = await GetResponseByUrl(url, need_header=True)
        resp = json.loads(resp)["Response"]
        return resp['membershipId']
    except:
        ACCESS.debug("getMembershipIDBySteamID出错")
        return None


async def getSteamIDByMembershipID(membershipid):
    """
    通过MembershipID获取用户的SteamID

    Args:
        membershipid
    Returns:
        SteamID
    """
    try:
        url = f"https://www.bungie.net/en/Profile/{membershipid}"
        data = await GetResponseByUrl(url)
        soup = BeautifulSoup(data, 'html.parser')
        result = soup.find(
            class_='inner-text-content').find(class_='title').get_text()
        steamid_pattern = re.compile(r"7656[0-9]{13}")
        return steamid_pattern.search(result).group(0)
    except:
        ACCESS.debug("getSteamIDByMembershipID出错")
        return None


async def getUsernameByMembershipid(membershipid):
    """
    根据用户的MembershipID获取用户的昵称

    Args:
        membershipId
    Returns:
        UserName
    """
    try:
        url = ROOT + f"/User/GetMembershipsById/{membershipid}/-1/"
        resp = await GetResponseByUrl(url, need_header=True)
        resp = json.loads(resp)["Response"]
        return resp['destinyMemberships'][0]['LastSeenDisplayName']
    except:
        ACCESS.debug("getUsernameByMembershipid出错")
        return None


async def getUserRaidReportByCharacterID(characterID, destinyMembershipId, membershipType="3"):
    """
    根据characterid获取角色的raid信息

    Args:
        characterID
        destinyMembershipId
        membershipType
    Returns:
        list类型结果信息
    """
    url = ROOT + \
        f"/Destiny2/{membershipType}/Account/{destinyMembershipId}/Character/{characterID}/Stats/Activities/?count=250&mode=raid&page=0"
    try:
        resp = await GetResponseByUrl(url, need_header=True)
    except:
        ACCESS.debug("获取角色CharacterID出错")
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
            ACCESS.debug("CharacterID，读取用户信息出错")
            return None
        return raid_data
    else:
        return None


async def getUserRaidReportByMemberShipID(destinyMembershipId, UserName, membershipType="3"):
    """
    通过MembershipID获取用户的Raid信息

    Args:
        destinyMembershipId
        UserName:用户昵称，用于组织返回信息
        membershipType
    Returns:
        组织完的Raid信息
    """
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
        ACCESS.debug(f"查询{UserName},{destinyMembershipId}Raid信息出错")
        return "查询出错，请稍后再试"


async def getPlayerdataBySteamID(steamid, UserName, season=current_season):
    """
    根据SteamID获取用户ELO信息

    Args:
        steamid
        UserName:用户昵称，用于组织返回信息
        season:赛季信息，默认为当前赛季
    Returns:
        组织完的ELO信息
    """
    url = f"https://api.tracker.gg/api/v2/destiny-2/standard/profile/steam/{steamid}/segments/playlist?season={season}"
    try:
        response = await urllibRequestGet(url)
        data = json.loads(response)['data']
    except:
        ACCESS.debug(f"查询{UserName}，{steamid}ELO信息出错")
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
    """
    根据MembershipID获取用户火力战队的成员信息

    Args:
        destinyMembershipId
        membershipType
    Returns:
        用户火力战队的成员的MembershipID的list
    """
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
    """
    根据MembershipID获取用户火力战队成员的Raid信息

    Args:
        destinyMembershipId
        membershipType
    Returns:
        组织完的信息
    """
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
    """
    根据MembershipID获取用户火力战队成员的ELO信息

    Args:
        MembershipID
        membershipType
    Returns:
        组织完的信息
    """
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
    """
    根据用户昵称获取用户的MembershipID，不推荐使用，可能有重名，也可能有BUG，Bungie老传统了

    Args:
        name:用户昵称
        membershipType:默认为“-1”，全平台搜索
    Returns:
        搜寻到的MembershipID，若不存在或者重名，则返回None
    """
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
        ACCESS.debug(f"{name}，查询用户membershipID出错")
        return None
