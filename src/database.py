from src.MY_CONST import *
import asyncio
import aiomysql


async def conn_db():
    """
    连接MySQL数据库

    Args:
        None
    Returns:
        connect
    """
    try:
        conn = await aiomysql.connect(host=db_host, port=db_port,
                                      user=db_username, password=db_passwd,
                                      db="wechat")
        return conn
    except:
        ACCESS.debug("连接MySQL出错")
        return None


async def save_data(wechatid, steamid, membershipid, username, Authority="guest"):
    """
    保存用户绑定数据

    Args:
        wechatid:微信用户OpenID
        steamid:
        membershipId:
        username:用户昵称
    Returns:
        True/False
    """
    conn = await conn_db()
    if conn == None:
        return False
    cursor = await conn.cursor()

    sql = """INSERT INTO UserData
        (wechatid,steamid,membershipid,username,Authority)
            VALUES ('%s','%s','%s','%s','%s')
            ON DUPLICATE KEY UPDATE steamid='%s',membershipid='%s',username='%s',Authority='%s'""" \
        % (wechatid, steamid, membershipid, username, Authority, steamid, membershipid, username, Authority)
    try:
        await cursor.execute(sql)
        await conn.commit()

        await cursor.close()
        conn.close()

        return True
    except:
        # 发生错误时回滚
        ACCESS.debug(f"{wechatid},{steamid},{membershipId},{username},数据库存储出错")
        await conn.rollback()
        await cursor.close()
        conn.close()
        return False


async def save_data_image(name, media_id, created_time, choose):
    """
    保存临时图片信息

    Args:
        name:图片名称
        media_id:图片素材的MEDIA_ID
        created_time:创建的时间，以便判断是否在有效期
        choose:保存的数据类型，详情见"./MY_CONST.py" "choose_list" 项
    Returns:
        True/False
    """
    if choose not in choose_list:
        ACCESS.debug("save_data_image,选择出错")
        return False
    conn = await conn_db()
    if conn == None:
        return False
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
        ACCESS.debug(f"{name},{media_id},{created_time},{choose},数据库保存出错")
        await conn.rollback()
        await cursor.close()
        conn.close()
        return False


async def FindUserDataByWchatID(wechatid):
    """
    查询用户绑定信息

    Args:
        wechatid:微信用户OpenID
    Returns:
        返回查询到的信息
    """
    conn = await conn_db()
    if conn == None:
        return False
    cursor = await conn.cursor()

    sql = """SELECT * FROM UserData WHERE wechatid='%s'""" \
        % (wechatid)

    try:
        await cursor.execute(sql)
        data = await cursor.fetchone()
        await cursor.close()
        conn.close()
    except:
        ACCESS.debug(f"MySQL查询用户出错：{wechatid}")
        return None
    return data


async def FindImageByName(name, choose):
    """
    查询图片信息

    Args:
        name:图片名称
        choose:保存的数据类型，详情见"./MY_CONST.py" "choose_list" 项
    Returns:
        返回查询到的信息
    """
    if choose not in choose_list:
        ACCESS.debug("FindImageByName,选择出错")
        return False

    conn = await conn_db()
    if conn == None:
        return False
    cursor = await conn.cursor()

    sql = """SELECT * FROM %s WHERE name='%s'""" \
        % (choose, name)
    try:
        await cursor.execute(sql)
        data = await cursor.fetchone()
        await cursor.close()
        conn.close()
    except:
        ACCESS.debug(f"{name},{choose},MySQL查询图片出错")
        return None
    return data


async def save_permanent_data(name, media_id):
    """
    保存永久图片信息

    Args:
        name:图片名称
        media_id:图片素材的MEDIA_ID
    Returns:
        True/False
    """
    conn = await conn_db()
    if conn == None:
        return False
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
        ACCESS.debug(f"{name},{media_id}保存永久图片出错")
        await conn.rollback()
        await cursor.close()
        conn.close()
        return False


async def FindSavedPermanent_all():
    """
    查询所有保存的永久图片信息

    Args:
        None
    Returns:
        查询到的信息
    """
    conn = await conn_db()
    if conn == None:
        return None
    cursor = await conn.cursor()

    sql = """SELECT * FROM permanent"""
    try:
        await cursor.execute(sql)
        data = await cursor.fetchall()
        await cursor.close()
        conn.close()
    except:
        ACCESS.debug("查询所有永久图片出错")
        return None
    return data
