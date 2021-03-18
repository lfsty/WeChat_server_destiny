from src.MY_CONST import *
import src.destiny_api
import xmltodict
import time
import json
import asyncio


async def response(xml_data):
    dict_data = xmltodict.parse(xml_data)['xml']  # 进行XML解析
    msg_type = dict_data['MsgType']
    wechat_id = dict_data['FromUserName']
    # 判断内容是否为文字
    if msg_type == "text":
        msg_id = dict_data['MsgId']
        content_list = dict_data['Content'].split(" ")
        resp_content = await TextHandler(wechat_id, content_list)
        # resp_content = dict_data['Content']
    # 消息类型为关注或取关
    elif msg_type == "event":
        if dict_data['Event'] == "subscribe":
            resp_content = help
        else:
            return None
    else:
        resp_content = "请输入文本"

    resp_data = {
        'xml': {
            "ToUserName": dict_data['FromUserName'],
            "FromUserName": dict_data['ToUserName'],
            "CreateTime": int(time.time()),
            "MsgType": 'text',
            "Content": resp_content,
        }
    }
    return xmltodict.unparse(resp_data)


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
            if xur_location == None:
                resp_content = "xur消失了"
            else:
                xur_saleitems = await src.destiny_api.getXurSaleItems()
                resp_content = f"位置：{xur_location}"
                for item in xur_saleitems:
                    resp_content += "\n-------------\n"
                    resp_content += item
                resp_content += "\n-------------"
    #     # 参数为raid，查看raid记录
    #     elif content_list[0] == "raid":
    #         data = FindUserDataByWchatID(wechat_id)
    #         if data != None:
    #             SteamID = data[1]
    #             MembershipID = data[2]
    #             UserName = data[3]
    #             RaidReport = await destiny.getUserRaidReportByMemberShipID(
    #                 MembershipID, UserName)
    #             if RaidReport != "error":
    #                 resp_content = RaidReport
    #             else:
    #                 resp_content = "查询出错，请稍后再试"
    #         else:
    #             resp_content = "尚未绑定账号"
    #     # 参数为elo，查看elo记录
    #     elif content_list[0] == "elo":
    #         data = FindUserDataByWchatID(wechat_id)
    #         if data != None:
    #             SteamID = data[1]
    #             MembershipID = data[2]
    #             UserName = data[3]
    #             # PlayerData = await destiny.getPlayerdataBySteamID(SteamID,UserName)
    #             resp_content = await destiny.getPlayerdataBySteamID(SteamID, UserName)
    #         else:
    #             resp_content = "尚未绑定账号"
    #     elif content_list[0] == "涩图":
    #         resp_content = "呵呵..."
    #     else:
    #         resp_content = help
    # # 有两个参数
    # elif len(content_list) == 2:
    #     # 指令为绑定
    #     if content_list[0] == "绑定":
    #         if destiny.is_steamid64(content_list[1]):
    #             SteamID = content_list[1]
    #             MembershipID = await destiny.getMembershipIDBySteamID(SteamID)
    #             UserName = await destiny.getUsernameByMenbershipid(MembershipID)
    #             if save_data(wechat_id, SteamID, MembershipID, UserName):
    #                 resp_content = "绑定账号成功"
    #             else:
    #                 resp_content = "绑定账号失败"
    #         else:
    #             resp_content = "请输入正确的Steamid"
    #     # 指令为elo
    #     elif content_list[0] == "elo":
    #         if destiny.is_steamid64(content_list[1]):
    #             SteamID = content_list[1]
    #             MembershipID = await destiny.getMembershipIDBySteamID(SteamID)
    #             UserName = await destiny.getUsernameByMenbershipid(MembershipID)
    #             # PlayerData = await destiny.getPlayerdataBySteamID(SteamID)
    #             resp_content = await destiny.getPlayerdataBySteamID(SteamID, UserName)
    #         else:
    #             resp_content = "请输入正确的Steamid"
    #     # 指令为raid
    #     elif content_list[0] == "raid":
    #         if destiny.is_steamid64(content_list[1]):
    #             SteamID = content_list[1]
    #             MembershipID = await destiny.getMembershipIDBySteamID(SteamID)
    #             UserName = await destiny.getUsernameByMenbershipid(MembershipID)
    #             RaidReport = await destiny.getUserRaidReportByMemberShipID(MembershipID, UserName)
    #             if RaidReport != "error":
    #                 resp_content = RaidReport
    #             else:
    #                 resp_content = "查询出错，请稍后再试"
    #         else:
    #             resp_content = "请输入正确的Steamid"
    #     # 指令为队友
    #     elif content_list[0] == "队友":
    #         if content_list[1] == "raid":
    #             data = FindUserDataByWchatID(wechat_id)
    #             if data != None:
    #                 SteamID = data[1]
    #                 MembershipID = data[2]
    #                 UserName = data[3]
    #                 # resp_content = await destiny.getPartyMembersRaidReport(MembershipID)
    #                 resp_content = await destiny.thread_getPartyMembersRaidReport(MembershipID)
    #                 if resp_content == None:
    #                     resp_content = "账号不在线"
    #             else:
    #                 resp_content = "尚未绑定账号"
    #         elif content_list[1] == "elo":
    #             data = FindUserDataByWchatID(wechat_id)
    #             if data != None:
    #                 SteamID = data[1]
    #                 MembershipID = data[2]
    #                 UserName = data[3]
    #                 # resp_content = await destiny.getPartyMembersRaidReport(MembershipID)
    #                 resp_content = await destiny.getPartyMembersElo(MembershipID)
    #                 if resp_content == None:
    #                     resp_content = "账号不在线"
    #             else:
    #                 resp_content = "尚未绑定账号"
    #         else:
    #             resp_content = "请输入正确的指令"
    #     else:
    #         resp_content = help
    # # 有三个参数
    # elif len(content_list) == 3:
    #     if content_list[0] == "elo" and content_list[1] == "赛季":
    #         season = get_Season(content_list[2])
    #         if season == "error":
    #             resp_content = "赛季输入出错"
    #         else:
    #             data = FindUserDataByWchatID(wechat_id)
    #             if data != None:
    #                 SteamID = data[1]
    #                 MembershipID = data[2]
    #                 UserName = data[3]
    #                 # PlayerData = await destiny.getPlayerdataBySteamID(SteamID, season)
    #                 resp_content = await destiny.getPlayerdataBySteamID(SteamID, UserName, season)
    #             else:
    #                 resp_content = "尚未绑定账号"
    #     # elif content_list[0] == "队友":
    #     #     if content_list[1] == "raid":
    #     #         if destiny.is_bungie_membershipid(content_list[2]):
    #     #             resp_content = await destiny.thread_getPartyMembersRaidReport(content_list[2])
    #     #             if resp_content == None:
    #     #                 resp_content = "账号不在线"
    #     #         else:
    #     #             resp_content = "请输入正确ID"
    #     #     else:
    #     #         resp_content = "请输入正确指令"
    #     else:
    #         resp_content = help
    # elif len(content_list) == 4:
    #     if content_list[0] == "elo" and content_list[2] == "赛季":
    #         if destiny.is_steamid64(content_list[1]):
    #             season = get_Season(content_list[3])
    #             if season == "error":
    #                 resp_content = "赛季输入出错"
    #             else:
    #                 SteamID = content_list[1]
    #                 MembershipID = await destiny.getMembershipIDBySteamID(SteamID)
    #                 UserName = await destiny.getUsernameByMenbershipid(MembershipID)
    #                 # PlayerData = await destiny.getPlayerdataBySteamID(
    #                 #     SteamID, season)
    #                 resp_content = await destiny.getPlayerdataBySteamID(SteamID, UserName, season)
    #         else:
    #             resp_content = "SteamID出错"
    # 五个及以上参数
    else:
        resp_content = help

    return resp_content
