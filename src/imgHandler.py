from src.MY_CONST import *
import src.database
import asyncio
import requests
import json
import time
import src.accessToken
import os


async def getDaily():
    name = time.strftime("%Y-%m-%d", time.localtime())
    files = os.listdir("./images/daily/")
    full_path = f"./images/daily/{name}.png"
    try:
        if f"{name}.png" in files:
            # 本地已存在日报文件
            data = await src.database.FindDailyByName(name)
            if data != None:
                return data[1]
            else:
                resp = await uploadImageToWeChat(full_path)
                media_id = resp["media_id"]
                created_time = resp["created_at"]
                await src.database.save_data_daily(name, media_id, created_time)
                return media_id
        else:
            await downloadDaily()
            resp = await uploadImageToWeChat(full_path)
            media_id = resp["media_id"]
            created_time = resp["created_at"]
            await src.database.save_data_daily(name, media_id, created_time)
            return media_id
    except:
        return None


async def uploadImageToWeChat(filepath):
    access_token = await src.accessToken.getAccessToken()
    img_upload_url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"
    with open(filepath, "rb") as f:
        files = {"media": f}
        resp = json.loads(requests.post(img_upload_url, files=files).text)
    return resp


async def downloadDaily():
    url = "http://www.tianque.top/d2api/today/"
    data = json.loads(requests.get(url).text)
    img_name = data["img_name"]
    img_url = data["img_url"]
    with open(f'./images/daily/{img_name}', 'wb') as f:
        resp = requests.get(img_url)
        f.write(resp.content)
