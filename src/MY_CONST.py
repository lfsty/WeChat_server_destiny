import json
import logging
import os
api_key = ""
ROOT = ""
proxy = ""
help = ""

with open("./data/main_data.json", "r") as f:
    data = json.load(f)
    try:
        api_key = data["destiny_api"]["api_key"]
        ROOT = data["destiny_api"]["root"]
        if "proxy" in data:
            proxy = data["proxy"]
        db_host = data["database"]["db_host"]
        db_username = data["database"]["db_username"]
        db_passwd = data["database"]["db_passwd"]
        db_port = data["database"]["db_port"]
        wechat_appID = data["wechat"]["appID"]
        appsecret = data["wechat"]["appsecret"]
    except:
        print("destiny_api.json文件读取出错")
        os._exit(0)

# 读取帮助信息
try:
    with open("./data/help.txt", "r") as f:
        data = f.readlines()
    for line in data:
        help += line
except:
    help = "help error"

choose_list = ["weekly", "daily", "Osiris", "xur", "permanent"]
xur = ["老九", "老玖", "xur"]
with open("./data/destiny_data.json", "r") as f:
    main_data = json.load(f)
    season_list = main_data["season"]
    current_season = main_data["current_season"]
    xur_location = main_data["xur_location"]
    entry_name = main_data["entry_name"]
    permanent_image_name = main_data["permanent"]

remain = {"Control": "占领", "Iron Banner": "铁骑",
          "Survival": "生存", "Trials of Osiris": "试炼"}

with open("./Manifest/DestinyInventoryItemDefinition.json", "r") as f:
    ItemDefinition = json.load(f)

with open("./Manifest/DestinyActivityDefinition.json", "r") as f:
    ActivityDefinition = json.load(f)


access = logging.getLogger("access")
# 定制logger的输出格式
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
# 创建日志：文件日志，终端日志
file_handler = logging.FileHandler('./log/access.log')
file_handler.setFormatter(formatter)
consle_handler = logging.StreamHandler()
consle_handler.setFormatter(formatter)
# 设置默认的日志级别,上线后推荐设置为Info,而不是Debug
access.setLevel(logging.INFO)
# 把文件日志和终端日志添加到日志处理器中
access.addHandler(file_handler)
