import json
import requests
import asyncio
import src.accessToken
import src.urlRequest


async def createMenu():
    access_token = await src.accessToken.getAccessToken()
    url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}"
    with open("./data/interface.json", "r") as f:
        data = json.load(f)
    resp = await src.urlRequest.PostResponse(url, data)
    print(resp)
