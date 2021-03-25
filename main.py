import tornado
import tornado.web
import tornado.ioloop
import hashlib
import asyncio
import json
import os
import src.response
import threading
import src.interface
TOKEN = ""


def check_signature(signature, timestamp, nonce):
    global TOKEN
    mylist = [TOKEN, timestamp, nonce]
    mylist.sort()
    string = "".join(mylist)
    sha1 = hashlib.sha1()
    sha1.update(string.encode('utf-8'))
    hashcode = sha1.hexdigest()
    if(signature == hashcode):
        return True
    else:
        return False


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        signature = self.get_argument('signature')
        timestamp = self.get_argument('timestamp')
        nonce = self.get_argument('nonce')
        echostr = self.get_argument('echostr')
        if check_signature(signature, timestamp, nonce):
            self.write(echostr)

    async def post(self):
        xml_data = self.request.body  # 获得post来的数据
        threading.Thread(target=src.response.thread_response,
                         args=(xml_data,)).start()
        self.write("success")


def LoadServerData():
    # 读取服务器配置文件
    with open(r"./data/main_data.json", "r") as f:
        ServerData = json.load(f)
        try:
            global TOKEN
            port = ServerData["server"]["port"]
            path = ServerData["server"]["path"]
            TOKEN = ServerData["server"]["TOKEN"]
        except:
            print("服务器配置读取失败")
            exit
    return port, path


if __name__ == "__main__":

    port, path = LoadServerData()
    application = tornado.web.Application([
        (path, MainHandler),
    ])
    application.listen(port)

    print("服务器启动成功...")

    tornado.ioloop.IOLoop.instance().start()
