from src.MY_CONST import *
import src.destiny_api
import src.database
import xmltodict
import time
import json
import asyncio
import src.accessToken
import src.urlRequest

def thread_response(xml_data):
    asyncio.run(response(xml_data))

async def sendDataToUser(msgtype,touser,content):
    resp_data = {
        "touser":touser,
        "msgtype":msgtype,
        "text":
        {
            "content":content
        }
    }
    access_token = await src.accessToken.getAccessToken()
    url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
    await src.urlRequest.PostResponse(url,resp_data)    


async def response(xml_data):
    dict_data = xmltodict.parse(xml_data)['xml']  # 进行XML解析
    msg_type = dict_data['MsgType']
    wechat_id = dict_data['FromUserName']
    await sendDataToUser("text",dict_data['FromUserName'],"收到消息，处理中...")
    # 判断内容是否为文字
    if msg_type == "text":
        msg_id = dict_data['MsgId']
        content_list = dict_data['Content'].split(" ")
        resp_content = await TextHandler(wechat_id, content_list)
    # 消息类型为关注或取关
    elif msg_type == "event":
        if dict_data['Event'] == "subscribe":
            resp_content = help
        else:
            return None
    else:
        resp_content = "请输入文本"

    await sendDataToUser("text",dict_data['FromUserName'],resp_content)


def get_Season(season_input):
    if season_input in season_list:
        season = season_list[season_input]
    else:
        try:
            if int(season_input) > current_season:
                raise Exception("Invalid season!")
            season = str(int(season_input))
        except:
            season = "error"
    return season


async def TextHandler(wechat_id, content_list):
    print(content_list)
    # 只有一个参数
    if len(content_list) == 1:
        # 参数为help，提供help
        if content_list[0] == "help":
            resp_content = help
        # 参数为老九，查询xur位置
        elif content_list[0] in xur:
            xur_location = await src.destiny_api.getXurLocation()
            if xur_location != "老九还没来":
                xur_saleitems = await src.destiny_api.getXurSaleItems()
                resp_content = f"位置：{xur_location}"
                for item in xur_saleitems:
                    resp_content += "\n-------------\n"
                    resp_content += item
                resp_content += "\n-------------"
        # 参数为raid，查看raid记录
        elif content_list[0] == "raid":
            data = await src.database.FindUserDataByWchatID(wechat_id)
            if data != None:
                SteamID = data[1]
                MembershipID = data[2]
                UserName = data[3]
                resp_content = await src.destiny_api.getUserRaidReportByMemberShipID(
                    MembershipID, UserName)
            else:
                resp_content = "尚未绑定账号"
        # 参数为elo，查看elo记录
        elif content_list[0] == "elo":
            data = await src.database.FindUserDataByWchatID(wechat_id)
            if data != None:
                SteamID = data[1]
                MembershipID = data[2]
                UserName = data[3]
                resp_content = await src.destiny_api.getPlayerdataBySteamID(SteamID, UserName)
            else:
                resp_content = "尚未绑定账号"
        elif content_list[0] == "涩图":
            resp_content = "呵呵..."
        else:
            resp_content = help
    # # 有两个参数
    elif len(content_list) == 2:
        # 指令为绑定
        if content_list[0] == "绑定":
            if src.destiny_api.is_steamid64(content_list[1]):
                SteamID = content_list[1]
                MembershipID = await src.destiny_api.getMembershipIDBySteamID(SteamID)
                if MembershipID == None:
                    return "MembershipID查询出错"
                UserName = await src.destiny_api.getUsernameByMenbershipid(MembershipID)
                if UserName == None:
                    return "UserName查询出错"
                if await src.database.save_data(wechat_id, SteamID, MembershipID, UserName):
                    resp_content = "绑定账号成功"
                else:
                    resp_content = "绑定账号失败"
            else:
                resp_content = "请输入正确的Steamid"
        # 指令为elo
        elif content_list[0] == "elo":
            if src.destiny_api.is_steamid64(content_list[1]):
                SteamID = content_list[1]
                MembershipID = await src.destiny_api.getMembershipIDBySteamID(SteamID)
                UserName = await src.destiny_api.getUsernameByMenbershipid(MembershipID)
                resp_content = await src.destiny_api.getPlayerdataBySteamID(SteamID, UserName)
            else:
                resp_content = "请输入正确的Steamid"
        # 指令为raid
        elif content_list[0] == "raid":
            if src.destiny_api.is_steamid64(content_list[1]):
                SteamID = content_list[1]
                MembershipID = await src.destiny_api.getMembershipIDBySteamID(SteamID)
                UserName = await src.destiny_api.getUsernameByMenbershipid(MembershipID)
                resp_content = await src.destiny_api.getUserRaidReportByMemberShipID(MembershipID, UserName)
            else:
                resp_content = "请输入正确的Steamid"
        # 指令为队友
        elif content_list[0] == "队友":
            if content_list[1] == "raid":
                data = await src.database.FindUserDataByWchatID(wechat_id)
                if data != None:
                    SteamID = data[1]
                    MembershipID = data[2]
                    UserName = data[3]
                    resp_content = await src.destiny_api.getPartyMembersRaidReport(MembershipID)
                else:
                    resp_content = "尚未绑定账号"
            elif content_list[1] == "elo":
                data = await src.database.FindUserDataByWchatID(wechat_id)
                if data != None:
                    SteamID = data[1]
                    MembershipID = data[2]
                    UserName = data[3]
                    resp_content = await src.destiny_api.getPartyMembersRaidReport(MembershipID)
                else:
                    resp_content = "尚未绑定账号"
        else:
            resp_content = help
    # 有三个参数
    elif len(content_list) == 3:
        if content_list[0] == "elo" and content_list[1] == "赛季":
            season = get_Season(content_list[2])
            if season == "error":
                resp_content = "赛季输入出错"
            else:
                data = await src.database.FindUserDataByWchatID(wechat_id)
                if data != None:
                    SteamID = data[1]
                    MembershipID = data[2]
                    UserName = data[3]
                    resp_content = await src.destiny_api.getPlayerdataBySteamID(SteamID, UserName, season)
                else:
                    resp_content = "尚未绑定账号"
        else:
            resp_content = help
    elif len(content_list) == 4:
        if content_list[0] == "elo" and content_list[2] == "赛季":
            if src.destiny_api.is_steamid64(content_list[1]):
                season = get_Season(content_list[3])
                if season == "error":
                    resp_content = "赛季输入出错"
                else:
                    SteamID = content_list[1]
                    MembershipID = await src.destiny_api.getMembershipIDBySteamID(SteamID)
                    UserName = await src.destiny_api.getUsernameByMenbershipid(MembershipID)
                    resp_content = await src.destiny_api.getPlayerdataBySteamID(SteamID, UserName, season)
            else:
                resp_content = "SteamID出错"
        else:
            resp_content = help
    # 五个及以上参数
    else:
        resp_content = help

    return resp_content
