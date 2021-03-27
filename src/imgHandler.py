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
    """
    获取日报的MEDIA_ID

    Args:
        None
    Returns:
        日报的MEDIA_ID或者错误返回None
    """
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
        ACCESS.debug("获取日报出错")
        return None


async def getWeekly():
    """
    获取周报的MEDIA_ID

    Args:
        None
    Returns:
        周报的MEDIA_ID或者错误返回None
    """
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
                ACCESS.debug("下载周报失败")
                return None
            return await bindAction(full_path, choose, name)
    except:
        ACCESS.debug("获取周报失败")
        return None


async def getXurOrOsiris(select):
    """
    获取XUR或Osiris的MEDIA_ID

    Args:
        select:"xur"或"Osiris"，选择所需要的图片
    Returns:
        XUR或Osiris的MEDIA_ID或者错误返回None
    """
    if select not in ["xur", "Osiris"]:
        ACCESS.debug("getXurOrOsiris,选择出错")
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
                    res = await downloadImage(entry_name[select], full_path, name)
                    if res == None:
                        return None
                except:
                    ACCESS.debug(f"下载{entry_name[select]}失败")
                    return None
                return await bindAction(full_path, choose, name)
        except:
            ACCESS.debug(f"获取{entry_name[select]}失败")
            return None
    else:
        return None


async def bindAction(full_path, choose, name):
    """
    上传图片至微信素材库与存储MEDIA_ID至MySQL数据库

    Args:
        full_path:完整的图片路径
        choose:选择图片类型
        name:图片名称
    Returns:
        日报的MEDIA_ID或者错误返回False
    """
    if choose not in choose_list:
        ACCESS.debug("bindAction,选择出错")
        return False

    resp = await uploadImageToWeChat(full_path)
    media_id = resp["media_id"]
    created_time = resp["created_at"]
    await src.database.save_data_image(name, media_id, created_time, choose)
    return media_id


async def uploadImageToWeChat(filepath):
    """
    上传图片至微信素材库，临时素材，有效期3天

    Args:
        filepath:完整的图片路径
    Returns:
        resp:post信息返回结果
    """
    access_token = await src.accessToken.getAccessToken()
    img_upload_url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"
    with open(filepath, "rb") as f:
        files = {"media": f}
        resp = json.loads(requests.post(img_upload_url, files=files).text)
    return resp


async def downloadDaily():
    """
    下载日报，感谢@天阙

    Args:
        None
    Returns:
        None
    """
    url = "http://www.tianque.top/d2api/today/"
    resp = await src.urlRequest.GetResponseByUrl(url)
    data = json.loads(resp)
    img_name = data["img_name"]
    img_url = data["img_url"]
    with open(f'./images/daily/{img_name}', 'wb') as f:
        resp = await src.urlRequest.GetResponseByUrl(img_url, content=True)
        f.write(resp)


async def downloadImage(name, full_path, current_time_name=None):
    """
    下载日报，感谢@seanalpha

    Args:
        name:下载图片的名称，参数为："命运2周报"或者"苏尔情报"或者"试炼周报"
        full_path:保存图片的完整路径
        current_time_name:当前时间，用于判断图片是否已更新
    Returns:
        None
    """
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
    if name_date != current_time_name:
        ACCESS.debug(f"{name}，尚未更新")
        return None
    resp = await src.urlRequest.GetResponseByUrl(entry_url)
    soup = BeautifulSoup(resp, 'html.parser')
    img_url = soup.find(class_="lazy").get("data-original")
    with open(full_path, 'wb') as f:
        resp = await src.urlRequest.GetResponseByUrl(img_url, content=True)
        f.write(resp)


async def uploadPermanentImageToWeChat(filepath):
    """
    上传永久图片素材至微信素材库

    Args:
        full_path:图片的完整路径
    Returns:
        resp:post信息返回结果
    """
    access_token = await src.accessToken.getAccessToken()
    img_upload_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
    with open(filepath, "rb") as f:
        files = {"media": f}
        resp = json.loads(requests.post(img_upload_url, files=files).text)
    return resp


async def updataPermanentImages():
    """
    更新"../images/permanent"目录下的图片素材，上传至微信素材库并保存相关信息至MySQL

    Args:
        None
    Returns:
        None
    """
    path = "./images/permanent/"
    files = os.listdir(path)
    saved_data = []
    items = await src.database.FindSavedPermanent_all()
    for item in items:
        saved_data.append(item[0])
    for item in files:
        file_path = path+item
        name = item[:-4]
        if name in saved_data:
            continue
        else:
            resp = await src.imgHandler.uploadPermanentImageToWeChat(file_path)
            media_id = resp["media_id"]
            await src.database.save_permanent_data(name, media_id)
