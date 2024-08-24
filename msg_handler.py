import asyncio
import func_timeout
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

import os

# import logging
# from logging.handlers import RotatingFileHandler

# # 设置日志基础配置
# logging.basicConfig(
#     level=logging.INFO,  # 日志级别
#     format='%(asctime)s [%(levelname)s] %(message)s',  # 日志格式
# )

# # 创建一个 rotating file handler，该handler可以将日志输出到文件，并在文件达到一定大小后进行切割
# handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=5)
# logger = logging.getLogger(__name__)
# logger.addHandler(handler)


class ItemBase(BaseModel):
    api: int
    wechat: str
    port: int
    pid: int
    msg: str
    errorCode: int
    errorMsg: Optional[str] = None
    data: dict


class MessageData_bytesExtra(BaseModel):
    userName: str
    thumb: Optional[str] = None
    image: Optional[str] = None
    file: Optional[str] = None
    roomNick: Optional[str] = None  # Make optional
    nickName: Optional[str] = None  # Make optional
    smallHeadImgUrl: Optional[str] = None  # Make optional and provide default value
    bigHeadImgUrl: Optional[str] = None  # Make optional and provide default value
    atuserlist: List[dict] = []  # Provide default empty list for optional list-type fields

class MessageData(BaseModel):
    sortIndex: int
    localId: int
    msgPrefixId: str
    msgSvrID: str
    userName: str
    nickName: str
    strContent: str
    msgSource: str
    createTime: int
    type: int
    subType: int
    isSender: int
    bytesExtra: MessageData_bytesExtra
    typeInfo: str
    smallHeadImgUrl: Optional[str]
    bigHeadImgUrl: Optional[str]
    isBizMsg: int
    isChatroom: Optional[bool] = None

class handler:
    def __init__(self,data:ItemBase) -> None:
        # if data.userName.find("@chatroom") != -1:
        #     data.append({"isChatroom": True})
        # else:
        #     data.append({"isChatroom": False})
        self.data=data



    async def answer_old_chino(self) -> None:
        from Chino_old.answer import answer as chino_old_main
        match  self.data.api:
            case 1005:
                msg_data=MessageData(**self.data.data)
                msg_data.isChatroom = msg_data.userName.find("@chatroom") != -1
                if msg_data.isSender!=1:
                    qu=msg_data.strContent   #消息内容
                    wxid=msg_data.userName  #消息发送人
                    wxid_group=""
                    if msg_data.isChatroom and msg_data.bytesExtra is not None:
                            byte=msg_data.bytesExtra
                            wxid_group =byte.userName
                    if os.path.exists("./Chino_old"):

                        await chino_old_main(wxid,wxid_group,qu)
                    else:
                        raise Exception("./Chino_old folder not found")
        # if os.path.exists("./Chino_old"):
        # else:
        #     with Popen(["python","./answer.py",wxid,wxid_group,qu], stdout=PIPE, stderr=STDOUT) as p, \
        #         open(f'./logs/wx_answer_{daytime}.log', 'ab+') as file:
        #         for line in p.stdout: # b'\n'-separated lines
        #             sys.stdout.buffer.write(line) # pass bytes as is
        #             file.write(line)
            #with open("wx_answer_out.log","a") as out, open("wx_answer_err.log","a") as err:
            #    subprocess.Popen(["python","./answer.py",wxid,wxid_group,qu],  # 需要执行的文件路径
            #                        stdout = out,
            #                        stderr = err,
            #                        bufsize=1)

    async def answer_satori(self) -> None:
        from .satori_adapter.adapter import queue
        from .satori_adapter.server import main
        await queue.put(self.data)
        await main()

async def async_wrapper(item):
    msgBot = handler(item)
    result = await msgBot.answer_old_chino()
    return result

# 保持为同步函数的外观，但内部调用异步操作
def sync_function(item):
    # asyncio.run() 在这里启动一个新的事件循环，并等待 async_wrapper() 完成
    result = asyncio.run(async_wrapper(item))
    return result




if __name__ == "__main__":

    item=ItemBase(**{"api":1005,"wechat":"wxid_wta02lbjszk622","port":28888,"pid":24256,"msg":"实时消息","errorCode":0,"errorMsg":"","data":{"sortIndex":1723309861000,"localId":0,"msgPrefixId":"0","msgSvrID":"8722562443880160169","userName":"wxid_2eokvnwm9a5a22","nickName":"树一只懒","strContent":"&bpixiv search kt=CLANNAD totalPage=1","msgSource":"<msgsource>\n    <sec_msg_node>\n        <alnode>\n            <fr>1</fr>\n        </alnode>\n    </sec_msg_node>\n    <pua>1</pua>\n    <signature>V1_WIyVu6jq|v1_WIyVu6jq</signature>\n    <tmp_node>\n        <publisher-id />\n    </tmp_node>\n</msgsource>\n","createTime":1723309861,"type":1,"subType":0,"isSender":0,"bytesExtra":{"userName":"","thumb":"","image":"","file":"","atuserlist":[]},"typeInfo":"文字","smallHeadImgUrl":"https://wx.qlogo.cn/mmhead/ver_1/8Nx7Zd2ccibQQlIef1k7mC725rf5ickdfYZd1eZtlrQXjFicmrMOwrcWoaeWnBKWxZOricah3LRV7LMdfZ04oibMy5929wad8kkTIqCsRI3iaRbQsfYibvt33ltd9RGicugLM4jic/132","bigHeadImgUrl":"https://wx.qlogo.cn/mmhead/ver_1/8Nx7Zd2ccibQQlIef1k7mC725rf5ickdfYZd1eZtlrQXjFicmrMOwrcWoaeWnBKWxZOricah3LRV7LMdfZ04oibMy5929wad8kkTIqCsRI3iaRbQsfYibvt33ltd9RGicugLM4jic/0","isBizMsg":0}})
    sync_function(item)
