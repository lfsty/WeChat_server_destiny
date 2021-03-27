from src.MY_CONST import *
import src.destiny_api
import src.database
import xmltodict
import time
import json
import asyncio
import src.accessToken
import src.urlRequest
import src.imgHandler


def thread_response(xml_data):
    """
    消息处理运行总入口
    """
    asyncio.run(response(xml_data))


def get_Season(season_input):
    """
    获取赛季信息

    Args: 
        season_input:用户赛季输入
    Returns:
        输入正确则返回对应赛季的字符串格式的数字，输入错误则返回“error”
    """
    if season_input in season_list:
        season = season_list[season_input]
    else:
        try:
            if int(season_input) > current_season:
                raise Exception("Invalid season!")
            season = str(int(season_input))
        except:
            ACCESS.debug("get_Season出错")
            season = "error"
    return season


async def sendDataToUser(msgtype, touser, content):
    """
    给用户发送消息，需要有微信平台客服返回消息权限，post方式

    Args:
        msgtype:消息格式，值为"text"或者"image"
        touser:接受消息用户，微信OpenID
        content:消息内容，文字信息或者mediaid
    Returns:
        None
    """
    resp_data = {}
    if msgtype == "text":
        resp_data = {
            "touser": touser,
            "msgtype": "text",
            "text":
            {
                "content": content
            }
        }
    elif msgtype == "image":
        resp_data = {
            "touser": touser,
            "msgtype": "image",
            "image":
            {
                "media_id": content
            }
        }
    if resp_data != {}:
        access_token = await src.accessToken.getAccessToken()
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        resp = await src.urlRequest.PostResponse(url, resp_data)
        resp = json.loads(resp)
        if resp["errmsg"] != "ok":
            ACCESS.debug(resp["errmsg"])


async def response(xml_data):
    """
    对用户信息进行解析和处理

    Args:
        xml_data:微信发送的源xml数据
    Returns:
        None
    """
    dict_data = xmltodict.parse(xml_data)['xml']  # 进行XML解析
    msg_type = dict_data['MsgType']
    wechat_id = dict_data['FromUserName']
    # 判断内容是否为文字
    if msg_type == "text":
        msg_id = dict_data['MsgId']
        content_list = dict_data['Content'].split(" ")
        resp_content, msgtype = await TextHandler(wechat_id, content_list)
    # 消息类型为关注或取关
    elif msg_type == "event":
        if dict_data['Event'] == "subscribe":
            msgtype = "text"
            resp_content = help
        elif dict_data['Event'] == "CLICK":
            EventKey = dict_data["EventKey"]
            resp_content, msgtype = await EventKeyHandler(wechat_id, EventKey)
        else:
            return None
    else:
        msgtype = "text"
        resp_content = "请输入文本"

    await sendDataToUser(msgtype, dict_data['FromUserName'], resp_content)


async def TextHandler(wechat_id, content_list):
    """
    用户发送为文字信息，对文字信息进行处理

    Args:
        wechat_id:微信用户OpenID
        content_list:用户发送的消息以“ ”（空格）拆分，list类型
    Returns:
        resp_content:消息内容
        msgtype:消息类型
    """
    ACCESS.info(f"{wechat_id}:{content_list}")
    # 只有一个参数
    if len(content_list) == 1:
        # 参数为help，提供help
        if content_list[0] == "help":
            msgtype = "text"
            resp_content = help
        # 参数为老九，查询xur位置
        elif content_list[0] in Options["xur_option"]:
            resp_content, msgtype = await getXur()
        # 参数为raid，查看raid记录
        elif content_list[0] in Options["raid_option"]:
            resp_content, msgtype = await getRaid(wechat_id=wechat_id)
        # 参数为elo，查看elo记录
        elif content_list[0] in Options["elo_option"]:
            resp_content, msgtype = await getElo(wechat_id=wechat_id)
        # 参数为elo，查看日报
        elif content_list[0] in Options["daily_option"]:
            resp_content, msgtype = await getDaily()
        # 参数为elo，查看周报
        elif content_list[0] in Options["weekly_option"]:
            resp_content, msgtype = await getWeekly()
        # 参数为试炼，查看试炼情报
        elif content_list[0] in Options["Osiris_option"]:
            resp_content, msgtype = await getOsiris()
        # 永久图片
        elif content_list[0] in Options["permanent_image_option"]:
            resp_content, msgtype = await getImages(content_list[0])
        elif content_list[0] == "强制刷新":
            resp_content, msgtype = await force_refresh(wechat_id)
        # 其他
        else:
            resp_content, msgtype = await elseData()
    # # 有两个参数
    elif len(content_list) == 2:
        # 指令为绑定
        if content_list[0] == "绑定":
            resp_content, msgtype = await bindData(steamid=content_list[1], wechat_id=wechat_id)
        # 指令为elo
        elif content_list[0] in Options["elo_option"]:
            resp_content, msgtype = await getElo(steamid=content_list[1], wechat_id=wechat_id)
        # 指令为raid
        elif content_list[0] in Options["raid_option"]:
            resp_content, msgtype = await getRaid(steamid=content_list[1], wechat_id=wechat_id)
        # 指令为队友
        elif content_list[0] == "队友":
            if content_list[1] in Options["raid_option"]:
                resp_content, msgtype = await getRaid(party=True, wechat_id=wechat_id)
            elif content_list[1] in Options["elo_option"]:
                resp_content, msgtype = await getElo(party=True, wechat_id=wechat_id)
        else:
            resp_content, msgtype = await elseData()
    # 有三个参数
    elif len(content_list) == 3:
        if content_list[0] in Options["elo_option"] and content_list[1] == "赛季":
            resp_content, msgtype = await getElo(wechat_id=wechat_id, season=content_list[2])
        else:
            resp_content, msgtype = await elseData()
    elif len(content_list) == 4:
        if content_list[0] in Options["elo_option"] and content_list[2] == "赛季":
            resp_content, msgtype = await getElo(steamid=content_list[1], season=content_list[3])
        else:
            resp_content, msgtype = await elseData()
    # 五个及以上参数
    else:
        resp_content, msgtype = await elseData()

    return resp_content, msgtype


async def returnWaitingMsg(wechat_id):
    """
    给用户发送等待消息

    Args:
        wechat_id:微信用户OpenID
    Returns:
        None
    """
    await sendDataToUser("text", wechat_id, "获取此信息时间可能较长，请稍后...")


async def EventKeyHandler(wechat_id, EventKey):
    """
    Event类型消息处理

    Args:
        wechat_id:微信用户OpenID
        EventKey:自定义的Event，详情见"./interface.py"
    Returns:
        resp_content:消息内容
        msgtype:消息类型
    """
    ACCESS.info(f"{wechat_id}:{EventKey}")
    if EventKey == "daily":
        resp_content, msgtype = await getDaily()
    elif EventKey == "weekly":
        resp_content, msgtype = await getWeekly()
    elif EventKey == "xur":
        resp_content, msgtype = await getXur()
    elif EventKey == "partyelo":
        resp_content, msgtype = await getElo(party=True, wechat_id=wechat_id)
    elif EventKey == "partyraid":
        resp_content, msgtype = await getRaid(party=True, wechat_id=wechat_id)
    elif EventKey == "meelo":
        resp_content, msgtype = await getElo(wechat_id=wechat_id)
    elif EventKey == "meraid":
        resp_content, msgtype = await getRaid(wechat_id=wechat_id)
    elif EventKey == "help":
        resp_content, msgtype = await elseData()
    elif EventKey == "Osiris":
        resp_content, msgtype = await getOsiris()
    elif EventKey in Options["permanent_image_option"]:
        resp_content, msgtype = await getImages(EventKey)
    return resp_content, msgtype


# async def getXur():
#     msgtype = "text"
#     xur_location = await src.destiny_api.getXurLocation()
#     if xur_location != "老九还没来":
#         xur_saleitems = await src.destiny_api.getXurSaleItems()
#         resp_content = f"位置：{xur_location}"
#         for item in xur_saleitems:
#             resp_content += "\n-------------\n"
#             resp_content += item
#         resp_content += "\n-------------"
#     return resp_content, msgtype


async def getRaid(wechat_id, steamid=None, party=False):
    """
    获取Raid信息

    Args:
        wechat_id:微信用户OpenID，用于给用户返回提示等待信息
        steamid:SteamID信息，根据SteamID查询用户记录，默认为None
        party:是否查询火力战队信息，bool类型，默认为False
    Returns:
        resp_content:消息内容
        msgtype:消息类型
    """
    msgtype = "text"
    await returnWaitingMsg(wechat_id)
    if not party:
        # 查询单人
        if steamid == None:
            # 查询自身
            data = await src.database.FindUserDataByWchatID(wechat_id)
            if data != None:
                SteamID = data[1]
                MembershipID = data[2]
                UserName = data[3]
                resp_content = await src.destiny_api.getUserRaidReportByMemberShipID(
                    MembershipID, UserName)
            else:
                resp_content = "尚未绑定账号"
        else:
            if src.destiny_api.is_steamid64(steamid):
                SteamID = steamid
                MembershipID = await src.destiny_api.getMembershipIDBySteamID(SteamID)
                UserName = await src.destiny_api.getUsernameByMembershipid(MembershipID)
                resp_content = await src.destiny_api.getUserRaidReportByMemberShipID(MembershipID, UserName)
            else:
                UserName = steamid
                MembershipID = await src.destiny_api.SearchUsersByName(UserName)
                if MembershipID != None:
                    resp_content = await src.destiny_api.getUserRaidReportByMemberShipID(MembershipID, UserName)
                else:
                    resp_content = "用户不存在或存在重名"
    else:
        # 查询火力战队
        if steamid == None:
            # 查询自身火力战队
            data = await src.database.FindUserDataByWchatID(wechat_id)
            if data != None:
                SteamID = data[1]
                MembershipID = data[2]
                UserName = data[3]
                resp_content = await src.destiny_api.getPartyMembersRaidReport(MembershipID)
            else:
                resp_content = "尚未绑定账号"
        else:
            # steamid火力战队
            resp_content = "该服务尚未开通"
            pass
    return resp_content, msgtype


async def getElo(wechat_id, steamid=None, party=False, season=current_season):
    """
    获取用户ELO信息

    Args:
        wechat_id:微信用户OpenID，用于给用户返回提示等待信息
        steamid:SteamID信息，根据SteamID查询用户记录，默认为None
        party:是否查询火力战队信息，bool类型，默认为False
        season:确定赛季信息，默认为当前赛季
    Returns:
        resp_content:消息内容
        msgtype:消息类型
    """
    msgtype = "text"
    if season != "13":
        season = get_Season(season)
        if season == "error":
            return "赛季输入出错", msgtype
    await returnWaitingMsg(wechat_id)
    if not party:
        # 查询单人
        if steamid == None:
            # 查询自身
            data = await src.database.FindUserDataByWchatID(wechat_id)
            if data != None:
                SteamID = data[1]
                MembershipID = data[2]
                UserName = data[3]
                resp_content = await src.destiny_api.getPlayerdataBySteamID(SteamID, UserName, season)
            else:
                resp_content = "尚未绑定账号"
        else:
            # 查询steamid
            if src.destiny_api.is_steamid64(steamid):
                SteamID = steamid
                MembershipID = await src.destiny_api.getMembershipIDBySteamID(SteamID)
                UserName = await src.destiny_api.getUsernameByMembershipid(MembershipID)
                resp_content = await src.destiny_api.getPlayerdataBySteamID(SteamID, UserName, season)
            else:
                UserName = steamid
                MembershipID = await src.destiny_api.SearchUsersByName(UserName)
                if MembershipID != None:
                    SteamID = await src.destiny_api.getSteamIDByMembershipID(MembershipID)
                    resp_content = await src.destiny_api.getPlayerdataBySteamID(SteamID, UserName, season)
                else:
                    resp_content = "用户不存在或存在重名"
    else:
        if steamid == None:
            data = await src.database.FindUserDataByWchatID(wechat_id)
            if data != None:
                SteamID = data[1]
                MembershipID = data[2]
                UserName = data[3]
                resp_content = await src.destiny_api.getPartyMembersElo(MembershipID)
            else:
                resp_content = "尚未绑定账号"
        else:
            # steamid火力战队
            resp_content = "该服务尚未开通"
            pass
    return resp_content, msgtype


async def getImages(name):
    """
    获取图片信息

    Args:
        name:地窖开车关/下水道/"破碎王座地图/许愿墙
    Returns:
        resp_content:图片的微信素材的MEDIA_ID或者错误信息
        msgtype:消息类型
    """
    msgtype = "image"
    name_en = Options["permanent_image_option"][name]
    return_data = await src.database.FindImageByName(name_en, "permanent")
    if return_data == None:
        resp_content = f"获取{name}出错"
        msgtype = "text"
    else:
        resp_content = return_data[1]
    return resp_content, msgtype


async def getDaily():
    """
    获取日报的MEDIA_ID

    Args:
        None
    Returns:
        resp_content:日报图片的微信素材的MEDIA_ID或者错误信息
        msgtype:消息类型
    """
    msgtype = "image"
    resp_content = await src.imgHandler.getDaily()
    if resp_content == None:
        resp_content = "获取日报出错"
        msgtype = "text"
    return resp_content, msgtype


async def getWeekly():
    """
    获取周报的MEDIA_ID

    Args:
        None
    Returns:
        resp_content:周报图片的微信素材的MEDIA_ID或者错误信息
        msgtype:消息类型
    """
    msgtype = "image"
    resp_content = await src.imgHandler.getWeekly()
    if resp_content == None:
        resp_content = "获取周报出错"
        msgtype = "text"
    return resp_content, msgtype


async def getXur():
    """
    获取XUR图片的MEDIA_ID

    Args:
        None
    Returns:
        resp_content:XUR图片的微信素材的MEDIA_ID或者错误信息
        msgtype:消息类型
    """
    msgtype = "image"
    resp_content = await src.imgHandler.getXurOrOsiris("xur")
    if resp_content == None:
        resp_content = "获取XUR情报出错或尚未更新"
        msgtype = "text"
    return resp_content, msgtype


async def getOsiris():
    """
    获取试炼的MEDIA_ID

    Args:
        None
    Returns:
        resp_content:试炼图片的微信素材的MEDIA_ID或者错误信息
        msgtype:消息类型
    """
    msgtype = "image"
    resp_content = await src.imgHandler.getXurOrOsiris("Osiris")
    if resp_content == None:
        resp_content = "获取试炼情报出错或尚未更新"
        msgtype = "text"
    return resp_content, msgtype


async def elseData():
    """
    获取帮助信息

    Args:
        None
    Returns:
        resp_content:help信息
        msgtype:"text"
    """
    msgtype = "text"
    resp_content = help
    return resp_content, msgtype


async def bindData(steamid, wechat_id):
    """
    绑定账号

    Args:
        steamid:需要绑定SteamID
        wechat_id:需要绑定的微信OpenID
    Returns:
        resp_content:提示信息
        msgtype:"text"
    """
    msgtype = "text"
    if src.destiny_api.is_steamid64(steamid):
        SteamID = steamid
        MembershipID = await src.destiny_api.getMembershipIDBySteamID(SteamID)
        if MembershipID == None:
            return "MembershipID查询出错", msgtype
        UserName = await src.destiny_api.getUsernameByMembershipid(MembershipID)
        if UserName == None:
            return "UserName查询出错", msgtype
        if await src.database.save_data(wechat_id, SteamID, MembershipID, UserName):
            resp_content = "绑定账号成功"
        else:
            resp_content = "绑定账号失败"
    else:
        UserName = steamid
        MembershipID = await src.destiny_api.SearchUsersByName(UserName)
        if MembershipID != None:
            SteamID = await src.destiny_api.getSteamIDByMembershipID(MembershipID)
            if await src.database.save_data(wechat_id, SteamID, MembershipID, UserName):
                resp_content = f"绑定账号成功,请确认SteamID是否正确,SteamID：{SteamID}"
            else:
                resp_content = "绑定账号失败"
        else:
            resp_content = "用户不存在或存在重名，请使用SteamID绑定"
    return resp_content, msgtype


async def force_refresh(wechat_id):
    msgtype = "text"
    resp_content = "您没有权限"
    data = await src.database.FindUserDataByWchatID(wechat_id)
    Authority = data[4]
    if Authority == "root":
        resp = await src.accessToken.refresh_access_token()
        if resp == False:
            return "刷新access_token失败", msgtype

        resp_content = "OK"
    return resp_content, msgtype
