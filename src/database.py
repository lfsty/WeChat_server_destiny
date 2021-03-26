from src.MY_CONST import *
import asyncio
import aiomysql


async def conn_db():
    conn = await aiomysql.connect(host=db_host, port=db_port,
                                  user=db_username, password=db_passwd,
                                  db="wechat")
    return conn


async def save_data(wechatid, steamid, membershipid, username):

    conn = await conn_db()
    cursor = await conn.cursor()

    sql = """INSERT INTO UserData
        (wechatid,steamid,membershipid,username)
            VALUES ('%s','%s','%s','%s')
            ON DUPLICATE KEY UPDATE steamid='%s',membershipid='%s',username='%s'""" \
        % (wechatid, steamid, membershipid, username, steamid, membershipid, username)
    try:
        await cursor.execute(sql)
        await conn.commit()

        await cursor.close()
        conn.close()

        return True
    except:
        # 发生错误时回滚
        await conn.rollback()
        await cursor.close()
        conn.close()
        return False


async def save_data_image(name, media_id, created_time, choose):
    if choose not in choose_list:
        print("choose出错")
        return False
    conn = await conn_db()
    cursor = await conn.cursor()

    sql = """INSERT INTO %s
        (name,media_id,created_time)
            VALUES ('%s','%s','%d')
            ON DUPLICATE KEY UPDATE media_id='%s',created_time='%d'""" \
        % (choose, name, media_id, created_time, media_id, created_time)
    try:
        await cursor.execute(sql)
        await conn.commit()

        await cursor.close()
        conn.close()

        return True
    except:
        # 发生错误时回滚
        await conn.rollback()
        await cursor.close()
        conn.close()
        return False


async def FindUserDataByWchatID(wechatid):

    conn = await conn_db()
    cursor = await conn.cursor()

    sql = """SELECT * FROM UserData WHERE wechatid='%s'""" \
        % (wechatid)

    try:
        await cursor.execute(sql)
        data = await cursor.fetchone()
        await cursor.close()
        conn.close()
    except:
        return None
    return data


async def FindImageByName(name, choose):
    if choose not in choose_list:
        print("choose出错")
        return False

    conn = await conn_db()
    cursor = await conn.cursor()

    sql = """SELECT * FROM %s WHERE name='%s'""" \
        % (choose, name)
    try:
        await cursor.execute(sql)
        data = await cursor.fetchone()
        await cursor.close()
        conn.close()
    except:
        return None
    return data


async def save_permanent_data(name, media_id):

    conn = await conn_db()
    cursor = await conn.cursor()

    sql = """INSERT INTO permanent
        (name,media_id)
            VALUES ('%s','%s')
            ON DUPLICATE KEY UPDATE media_id='%s'""" \
        % (name, media_id, media_id)
    try:
        await cursor.execute(sql)
        await conn.commit()

        await cursor.close()
        conn.close()

        return True
    except:
        # 发生错误时回滚
        await conn.rollback()
        await cursor.close()
        conn.close()
        return False


async def FindSavedPermanent():

    conn = await conn_db()
    cursor = await conn.cursor()

    sql = """SELECT * FROM permanent"""
    try:
        await cursor.execute(sql)
        data = await cursor.fetchall()
        await cursor.close()
        conn.close()
    except:
        return None
    return data
