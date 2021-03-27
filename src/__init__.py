import os
import asyncio
import pymysql
import json


# 程序运行的初始化操作
if not os.path.exists("./data/main_data.json"):
    print("main_data.json文件不存在...")
    os._exit(0)

if not os.path.exists("./data/destiny_data.json"):
    print("destiny_data.json文件不存在...")
    os._exit(0)


with open("./data/main_data.json", "r") as f:
    data = json.load(f)
    try:
        db_host = data["database"]["db_host"]
        db_username = data["database"]["db_username"]
        db_passwd = data["database"]["db_passwd"]
        db_port = data["database"]["db_port"]
    except:
        print("destiny_api.json文件读取出错")
        os._exit(0)

from warnings import filterwarnings
filterwarnings("ignore", category=pymysql.Warning)  # 忽略数据库警告

try:
    db = pymysql.connect(
        host=db_host,
        user=db_username,
        passwd=db_passwd,
        port=db_port
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
            username char(30),
            Authority char(10))"""
    cursor.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS daily ( 
            name char(15) NOT NULL PRIMARY KEY,
            media_id char(70),
            created_time int(10))"""
    cursor.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS weekly ( 
            name char(15) NOT NULL PRIMARY KEY,
            media_id char(70),
            created_time int(10))"""
    cursor.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS Osiris ( 
            name char(15) NOT NULL PRIMARY KEY,
            media_id char(70),
            created_time int(10))"""
    cursor.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS xur ( 
            name char(15) NOT NULL PRIMARY KEY,
            media_id char(70),
            created_time int(10))"""
    cursor.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS permanent ( 
            name char(20) NOT NULL PRIMARY KEY,
            media_id char(70))"""
    cursor.execute(sql)

    cursor.close()
    db.close()
except:
    print("初始化数据库出错")
    os._exit(0)

if not os.path.exists("./data/access_token.json"):
    with open("./data/access_token.json", "w+") as f:
        f.write("{}")

if not os.path.exists("./images"):
    os.makedirs("./images")

if not os.path.exists("./images/daily"):
    os.makedirs("./images/daily")

if not os.path.exists("./images/weekly"):
    os.makedirs("./images/weekly")

if not os.path.exists("./images/Osiris"):
    os.makedirs("./images/Osiris")

if not os.path.exists("./images/xur"):
    os.makedirs("./images/xur")

if not os.path.exists("./log"):
    os.makedirs("./log")
