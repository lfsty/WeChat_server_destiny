import requests
import asyncio
import os
import json
from src.MY_CONST import *


async def GetResponseByUrl(url, need_header=False):
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

    response = requests.get(url, proxies=proxies, headers=headers)
    return response.text
