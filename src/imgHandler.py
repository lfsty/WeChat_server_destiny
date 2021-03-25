from src.MY_CONST import *
import src.database
import asyncio
import src.urlRequest
import json
import src.accessToken
import os
from bs4 import BeautifulSoup
import datetime
import requests


async def getDaily():
    choose = "daily"
    name = datetime.datetime.now().strftime("%Y-%m-%d")
    files = os.listdir("./images/daily/")
    full_path = f"./images/daily/{name}.png"
    try:
        if f"{name}.png" in files:
            # 本地已存在日报文件
            data = await src.database.FindImageByName(name, choose)
            if data != None:
                return data[1]
            else:
                return await bindAction(full_path, choose, name)
        else:
            await downloadDaily()
            return await bindAction(full_path, choose, name)
    except:
        return None


async def getWeekly():
    choose = "weekly"
    today = datetime.datetime.now().weekday()
    if today >= 2:
        gap = today - 2
    else:
        gap = today + 4
    name = (datetime.datetime.now()-datetime.timedelta(days=gap)
            ).strftime("%Y-%m-%d")
    files = os.listdir("./images/weekly/")
    full_path = f"./images/weekly/{name}.jpg"
    try:
        if f"{name}.jpg" in files:
            # 本地已存在周报
            data = await src.database.FindImageByName(name, choose)
            if data != None:
                now_time = datetime.datetime.timestamp(datetime.datetime.now())
                media_id = data[1]
                created_time = data[2]
                if now_time - float(created_time) < 259200.0:
                    return media_id
                else:
                    return await bindAction(full_path, choose, name)
            else:
                return await bindAction(full_path, choose, name)
        else:
            try:
                await downloadImage("命运2周报", full_path)
            except:
                print("下载周报失败")
                return None
            return await bindAction(full_path, choose, name)
    except:
        return None


async def getXurOrOsiris(select):
    if select not in ["xur", "Osiris"]:
        print("select出错")
        return None
    choose = select
    today = datetime.datetime.now().weekday()
    lists = [0, 1, 5, 6]
    if today in lists:
        today = datetime.datetime.now().weekday()
        if today >= 5:
            gap = today - 5
        else:
            gap = today + 2
        name = (datetime.datetime.now()-datetime.timedelta(days=gap)
                ).strftime("%Y-%m-%d")
        files = os.listdir(f"./images/{select}/")
        full_path = f"./images/{select}/{name}.jpg"
        try:
            if f"{name}.jpg" in files:
                data = await src.database.FindImageByName(name, choose)
                if data != None:
                    now_time = datetime.datetime.timestamp(
                        datetime.datetime.now())
                    media_id = data[1]
                    created_time = data[2]
                    if now_time - float(created_time) < 259200.0:
                        return media_id
                    else:
                        return await bindAction(full_path, choose, name)
                else:
                    return await bindAction(full_path, choose, name)
            else:
                try:
                    await downloadImage(entry_name[select], full_path)
                except:
                    print(f"下载{entry_name[select]}失败")
                    return None
                return await bindAction(full_path, choose, name)
        except:
            return None
    else:
        return None


async def bindAction(full_path, choose, name):
    if choose not in choose_list:
        print("choose出错")
        return False

    resp = await uploadImageToWeChat(full_path)
    media_id = resp["media_id"]
    created_time = resp["created_at"]
    await src.database.save_data_image(name, media_id, created_time, choose)
    return media_id


async def uploadImageToWeChat(filepath):
    access_token = await src.accessToken.getAccessToken()
    img_upload_url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"
    with open(filepath, "rb") as f:
        files = {"media": f}
        resp = json.loads(requests.post(img_upload_url, files=files).text)
    return resp


async def downloadDaily():
    url = "http://www.tianque.top/d2api/today/"
    resp = await src.urlRequest.GetResponseByUrl(url)
    data = json.loads(resp)
    img_name = data["img_name"]
    img_url = data["img_url"]
    with open(f'./images/daily/{img_name}', 'wb') as f:
        resp = await src.urlRequest.GetResponseByUrl(img_url, content=True)
        f.write(resp)


async def downloadImage(name, full_path):
    url = "https://api.xiaoheihe.cn/wiki/get_homepage_content/?wiki_id=1085660&verison=&is_share=1"
    resp = await src.urlRequest.GetResponseByUrl(url)
    data = json.loads(resp)
    lists = data["result"]["chunk"][0]["block"][0]["tag_list"][1]["block_entries"]
    for item in lists:
        if item["entry_name"] == name:
            entry_url = item["entry_url"]
            name_date = item["id"].split(" - ")[1]
            name_date = datetime.datetime.strptime(
                name_date, '%Y.%m.%d').strftime("%Y-%m-%d")
            break
    resp = await src.urlRequest.GetResponseByUrl(entry_url)
    soup = BeautifulSoup(resp, 'html.parser')
    img_url = soup.find(class_="lazy").get("data-original")
    with open(full_path, 'wb') as f:
        resp = await src.urlRequest.GetResponseByUrl(img_url, content=True)
        f.write(resp)
