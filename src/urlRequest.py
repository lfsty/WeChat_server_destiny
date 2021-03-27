import requests
import asyncio
import os
import json
from src.MY_CONST import *
import urllib3


async def GetResponseByUrl(url, need_header=False, content=False):
    """
    Get获取网站数据

    Args:
        url:网站地址
        need_header:是否需要使用Bungie的API头，默认为False
        content:是否需要请求的二进制码，下载图片时需要，默认为False
    Returns:
        response:根据需求返回网络请求结果
    """
    if need_header:
        headers = {
            "X-API-Key": api_key,
        }
    else:
        headers = None

    if proxy != "":
        proxies = {"http": f"http://{proxy}",
                   "https": f"https://{proxy}", }
    else:
        proxies = None

    if content:
        response = requests.get(url, proxies=proxies, headers=headers).content
    else:
        response = requests.get(url, proxies=proxies, headers=headers).text
    return response


async def PostResponse(url, payload):
    """
    Post发送json数据，（微信平台）

    Args:
        url:目的地址
        payload:map类型数据
    Returns:
        response:post返回结果
    """
    response = requests.post(url, data=bytes(json.dumps(
        payload, ensure_ascii=False), encoding='utf-8'))
    return response.text


async def urllibRequestGet(url):
    """
    使用urllib3发送get请求，一般不调用此函数

    Args:
        url:目的地址
    Returns:
        response:请求结果返回
    """
    response = urllib3.PoolManager().request('GET', url).data.decode()
    return response
