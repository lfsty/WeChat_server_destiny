from src.urlRequest import *
import asyncio
import os
from tqdm import tqdm
from src.MY_CONST import *


async def getManifest(lang="zh-chs"):
    """
    下载Manifest

    Args:
        lang:语言选择，默认为简体中文
    Returns:
        None
    """
    try:
        url = ROOT + "/Destiny2/Manifest/"
        response = await GetResponseByUrl(url, need_header=True)
        response = json.loads(response)
    except:
        ACCESS.debug("获取Manifest出错")
        return None

    if not os.path.exists("./Manifest"):
        os.mkdir("./Manifest")

    with open("./Manifest/Manifest.json", "w") as f:
        json.dump(response, f)

    if lang in response['Response']["jsonWorldComponentContentPaths"]:
        jsons = response['Response']["jsonWorldComponentContentPaths"][lang]
        ACCESS.debug("下载Manifest")
        pbar_total = tqdm(total=len(jsons), desc="下载进度...")
        for item in jsons:
            url = "https://www.bungie.net/"+jsons[item]
            temp = await GetResponseByUrl(url, need_header=True)
            temp = json.loads(temp)
            with open("./Manifest/"+item+".json", "w") as f:
                json.dump(temp, f)
            pbar_total.update(1)
        pbar_total.close()
    else:
        ACCESS.debug("Manifest语言选择出错")
        return None
