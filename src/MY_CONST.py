import json

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
    except:
        print("destiny_api.json文件读取出错")
        exit

# 读取帮助信息
try:
    with open("./data/help.txt", "r") as f:
        data = f.readlines()
    for line in data:
        help += line
except:
    help = "help error"


xur = ["老九", "老玖", "xur"]
with open("./data/destiny_data.json", "r") as f:
    main_data = json.load(f)
    season_list = main_data["season"]
    current_season = main_data["current_season"]
    xur_location = main_data["xur_location"]

remain = {"Control": "占领", "Iron Banner": "铁骑",
          "Survival": "生存", "Trials of Osiris": "试炼"}

with open("./Manifest/DestinyInventoryItemDefinition.json", "r") as f:
    ItemDefinition = json.load(f)

with open("./Manifest/DestinyActivityDefinition.json", "r") as f:
    ActivityDefinition = json.load(f)
