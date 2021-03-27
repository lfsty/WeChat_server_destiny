import json
import requests
import asyncio
import src.accessToken
import src.urlRequest


async def createMenu():
    """
    发送微信公众号的自定义菜单栏请求，具体内容见"../data/interface.py"

    Args:
        None
    Returns:
        None
    直接print出post结果
    """
    access_token = await src.accessToken.getAccessToken()
    url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}"
    with open("./data/interface.json", "r") as f:
        data = json.load(f)
    resp = await src.urlRequest.PostResponse(url, data)
    print(resp)
