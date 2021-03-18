import os
import src.DownloadManifest
import asyncio
import pymysql


if not os.path.exists("./data/main_data.json"):
    print("main_data.json文件不存在...")
    exit

if not os.path.exists("./data/destiny_data.json"):
    print("destiny_data.json文件不存在...")
    exit

if not os.path.exists("./Manifest"):
    print("Manifest文件不存在，下载Manifest")
    if asyncio.run(src.DownloadManifest.getManifest()) == None:
        exit


from src.MY_CONST import *
try:
    db = pymysql.connect(
        host=db_host,
        user=db_username,
        passwd=db_passwd,
        port=db_port,
    )
    cursor = db.cursor()
    sql = """CREATE DATABASE IF NOT EXISTS wechat"""
    cursor.execute(sql)
    cursor.close()
    db.close()

    db = pymysql.connect(
        host=db_host,
        user=db_username,
        passwd=db_passwd,
        port=db_port,
        database="wechat",
    )
    cursor = db.cursor()
    sql = """CREATE TABLE IF NOT EXISTS UserData ( 
            wechatid char(30) NOT NULL PRIMARY KEY,
            steamid char(17),
            membershipid char(19),
            username char(30))"""
    cursor.execute(sql)
    cursor.close()
    db.close()
except:
    print("初始化数据库出错")
    exit
