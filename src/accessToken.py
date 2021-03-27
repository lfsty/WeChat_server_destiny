from src.MY_CONST import *
import os
import json
from src.urlRequest import *
import asyncio
import time


async def requestToken():
    """
    获取微信公众平台的access_token

    Args:
        None
    Returns:
        获取到的信息或者出错返回None
    """
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={wechat_appID}&secret={appsecret}"
        resp = await GetResponseByUrl(url)
        return json.loads(resp)
    except:
        ACCESS.debug("access_token获取出错")
        return None


def writeFile(access_token_json):
    """
    将获取到的access_token_json信息写入文件，以便后续调用

    Args:
        access_token_json:获取到的access_token信息
    Returns:
        None
    """
    with open("./data/access_token.json", "w") as f:
        now_time = time.time()
        data = {"access_token": access_token_json["access_token"],
                "get_time": now_time, "expires_in": access_token_json["expires_in"]}
        json.dump(data, f)


async def getAccessToken():
    """
    调用总入口，返回一个有效的access_token

    Args:
        None
    Returns:
        access_token
    """
    # 是否更新文件
    flag = False
    with open("./data/access_token.json", "r+") as f:
        try:
            data = json.load(f)
        except:
            ACCESS.debug("access_token.json文件读取失败")
            return None
        if data == {}:
            flag = True
        else:
            try:
                get_time = data["get_time"]
                expires_in = float(data["expires_in"])
                access_token = data["access_token"]
            except:
                ACCESS.debug("access_token文件内容读取失败")
                return None
            if time.time() - get_time - expires_in < 0:
                # access_token有效
                return access_token
            else:
                # 无效
                flag = True

    if flag:
        access_token_json = await requestToken()
        if access_token_json == None:
            return None
        else:
            try:
                writeFile(access_token_json)
                return access_token_json["access_token"]
            except:
                ACCESS.debug("access_token文件写入失败")
                return None
