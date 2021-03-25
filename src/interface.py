import json
import requests
import asyncio
import src.accessToken
import src.urlRequest


async def createMenu():
    access_token = await src.accessToken.getAccessToken()
    url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}"
    data = {
        "button": [
            {
                "name": "周/日报等",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "日报",
                        "key": "daily"
                    },
                    {
                        "type": "click",
                        "name": "周报",
                        "key": "weekly"
                    },
                    {
                        "type": "click",
                        "name": "XUR",
                        "key": "xur"
                    }]
            },
            {
                "name": "队友信息",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "elo",
                        "key": "partyelo"
                    },
                    {
                        "type": "click",
                        "name": "RaidReport",
                        "key": "partyraid"
                    }]
            }, {
                "name": "我",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "帮助",
                        "key": "help"
                    },
                    {
                        "type": "click",
                        "name": "elo",
                        "key": "meelo"
                    },
                    {
                        "type": "click",
                        "name": "RaidReport",
                        "key": "meraid"
                    }]
            }]
    }
    # resp = requests.post(url, data=json.dumps(data)).text
    resp = await src.urlRequest.PostResponse(url, data)
    print(resp)
