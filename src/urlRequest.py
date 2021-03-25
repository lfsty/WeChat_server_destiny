import requests
import asyncio
import os
import json
from src.MY_CONST import *
import urllib3


async def GetResponseByUrl(url, need_header=False, content=False):
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
    response = requests.post(url, data=bytes(json.dumps(
        payload, ensure_ascii=False), encoding='utf-8'))
    return response.text


async def urllibRequestGet(url):
    response = urllib3.PoolManager().request('GET', url).data.decode()
    return response
