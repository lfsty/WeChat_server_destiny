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
