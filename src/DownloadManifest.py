from src.urlRequest import *
import asyncio
import os
from tqdm import tqdm
from src.MY_CONST import *


async def getManifest(lang="zh-chs"):
    try:
        url = ROOT + "/Destiny2/Manifest/"
        response = await GetResponseByUrl(url, need_header=True)
        response = json.loads(response)
    except:
        print("获取Manifest出错")
        return None

    if not os.path.exists("./Manifest"):
        os.mkdir("./Manifest")

    with open("./Manifest/Manifest.json", "w") as f:
        json.dump(response, f)

    if lang in response['Response']["jsonWorldComponentContentPaths"]:
        jsons = response['Response']["jsonWorldComponentContentPaths"][lang]
        print("下载Manifest中...")
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
        print("语言选择出错")
        return None
