import json
import logging
import os
api_key = ""
ROOT = ""
proxy = ""
help = ""

# 定义日志


def get_logger(logger_name, log_file, level):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)

    return logging.getLogger(logger_name)


# 获取程序运行的主要信息
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
        log_level = data["log"]["level"]
        log_path = data["log"]["path"]
    except:
        ACCESS.debug("destiny_api.json文件读取出错")
        os._exit(0)
try:
    log_level_choose = {"INFO": logging.INFO, "DEBUG": logging.DEBUG}
    ACCESS = get_logger("access", log_path, log_level_choose[log_level])
except:
    print("log设置出错")
    os._exit(0)

# 读取帮助信息
try:
    with open("./data/help.txt", "r") as f:
        data = f.readlines()
    for line in data:
        help += line
except:
    ACCESS.debug("help error")
    help = "help error"

choose_list = ["weekly", "daily", "Osiris", "xur", "permanent"]
with open("./data/destiny_data.json", "r") as f:
    main_data = json.load(f)
    try:
        season_list = main_data["season"]
        current_season = main_data["current_season"]
        xur_location = main_data["xur_location"]
        entry_name = main_data["entry_name"]
        Options = main_data["options"]
    except:
        ACCESS.debug("destiny_data.json文件读取出错")
        os._exit(0)

# ELO保留的信息
remain = {"Control": "占领", "Iron Banner": "铁骑",
          "Survival": "生存", "Trials of Osiris": "试炼"}
