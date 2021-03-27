import os
from tqdm import tqdm
import json
import requests

try:
    with open("./data/main_data.json", "r") as f:
        data = json.load(f)
        api_key = data["destiny_api"]["api_key"]
except:
    print("main_data.json文件读取出错")
    os._exit(0)


def getResponse(url):
    headers = {
        "X-API-Key": api_key,
    }
    response = requests.get(url, headers=headers).content
    return response


def getManifest(lang="zh-chs"):
    """
    下载Manifest

    Args:
        lang:语言选择，默认为简体中文
    Returns:
        None
    """
    try:
        url = "https://www.bungie.net/Platform/Destiny2/Manifest/"
        response = getResponse(url)
        response = json.loads(response)
    except:
        return None

    if not os.path.exists("./Manifest"):
        os.mkdir("./Manifest")

    with open("./Manifest/Manifest.json", "w") as f:
        json.dump(response, f)

    if lang in response['Response']["jsonWorldComponentContentPaths"]:
        jsons = response['Response']["jsonWorldComponentContentPaths"][lang]
        print("下载Manifest")
        pbar_total = tqdm(total=len(jsons), desc="下载进度...")
        for item in jsons:
            url = "https://www.bungie.net/"+jsons[item]
            temp = getResponse(url)
            temp = json.loads(temp)
            with open("./Manifest/"+item+".json", "w") as f:
                json.dump(temp, f)
            pbar_total.update(1)
        pbar_total.close()
    else:
        return None


if __name__ == "__main__":
    if getManifest() == None:
        print("更新失败")
