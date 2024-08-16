import httpx
import file_action
from pydantic import BaseModel
from .standard_print import printerr ,logger
from typing import List, Optional


class PostSendItem(BaseModel):
    api: int
    data: dict


class Request:
    def __init__(self, api: int, data: dict) -> None:
        connection = self.connection()
        self.url = f"http://{connection.host}:{connection.port}/"
        self.api = api
        self.data = data

    def connection(self):
        config = file_action.config_read()
        connection = config.connect
        return connection

    async def _send(self) -> dict:
        # Create an instance of PostSendItem
        post_data = PostSendItem(api=self.api, data=self.data)

        logger.debug(f"[Res_Send] {post_data}")

        # Convert the Pydantic model to a dictionary for sending as JSON
        json_data = post_data.model_dump()

        # Use httpx to send a POST request
        try:
            timeout=httpx.Timeout(240)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(self.url, json=json_data)
                response.raise_for_status()  # This will raise an exception for 4XX/5XX responses
                response_data = response.json()
                logger.debug(f"[Res_Receive] {response_data}")
                return response_data
        except httpx.HTTPStatusError as e:
            error = {
                "error": f"HTTP Error: {e.response.status_code}, Message: {e.response.text}"
            }
            printerr(str(error))
            return error
        except Exception as e:
            error = {"error": str(e)}
            printerr(str(error))
            return error

    @classmethod
    async def fetch(cls, api: int, data: dict):
        instance = cls(api, data)
        return await instance._send()


class DynamicModel(BaseModel):
    class Config:
        extra = extra = "allow"


class ApiReturn_base(BaseModel):
    api: int
    wechat: str
    port: int
    pid: int
    msg: str
    errorCode: int
    errorMsg: str
    data: DynamicModel



# 消息功能
class ApiReturn_msg(ApiReturn_base):
    pass


class send_msg():
    # https://www.showdoc.com.cn/wx3api/9346615465192672
    @staticmethod
    async def text(
        userName: str, content: str, isUnicodeEscape: int = 1
    ) -> ApiReturn_msg:
        return ApiReturn_msg(
            **await Request.fetch (
                2200,
                {
                    "isUnicodeEscape": isUnicodeEscape,
                    "content": content,
                    "userName": userName,
                },
            )
        )

    # https://www.showdoc.com.cn/wx3api/9346612137380535
    @staticmethod
    async def image(userName: str, imgFileName: str) -> ApiReturn_msg:
        return ApiReturn_msg(
            **await Request.fetch(2201, {"imgFileName": imgFileName, "userName": userName})
        )

    @staticmethod
    async def file(userName: str, fileName: str) -> ApiReturn_msg:
        return ApiReturn_msg(
            **await Request.fetch(2202, {"fileName": fileName, "userName": userName})
        )

    @staticmethod
    async def gif(userName: str, gifFileName: str) -> ApiReturn_msg:
        return ApiReturn_msg(
            **await Request.fetch(2203, {"gifFileName": gifFileName, "userName": userName})
        )

    @staticmethod
    async def url(
        userName: str, url: str, title: str, thumbUrl: str, des: str
    ) -> ApiReturn_msg:
        return ApiReturn_msg(
            **await Request.fetch(
                2204,
                {
                    "des": des,
                    "userName": userName,
                    "thumbUrl": thumbUrl,
                    "title": title,
                    "url": url,
                },
            )
        )

    @staticmethod
    async def xml(userName: str, xml: str) -> ApiReturn_msg:
        return ApiReturn_msg(**await Request.fetch(2205, {"xml": xml, "userName": userName}))

    @staticmethod
    async def quote(userName: str, content: str, param: str, type: int) -> ApiReturn_msg:
        """_summary_

        Args:
            userName (str): _description_
            content (str): _description_
            param (str): _description_
            type (int): ype: 1 文本 ， 3 图片XML ，47 动态表情XML ， 49 文件 链接 小程序XML

        Returns:
            _type_: _description_
        """
        return ApiReturn_msg(
            **await Request.fetch(
                2206,
                {
                    "content": content,
                    "userName": userName,
                    "param": param,
                    "type": type,
                },
            )
        )

    @staticmethod
    async def fav(userName: str, favLocalID: int) -> ApiReturn_msg:
        return ApiReturn_msg(
            **await Request.fetch(2207, {"favLocalID": favLocalID, "userName": userName})
        )


# #https://www.showdoc.com.cn/wx2api/8905086274002428
# def send_xml(wxid,content):
#     return await Request.fetch("post",101,{"api": 101,"recverWxid": wxid,"content":content})

# #https://www.showdoc.com.cn/wx2api/8905087650547309
# def send_art(des,wxid,thumbUrl,title,url):
#     return await Request.fetch("post",10,{"api": 10,"des": des, "recverWxid": wxid,"thumbUrl": thumbUrl,"title": title,"url": url})

# #https://www.showdoc.com.cn/wx2api/8905149941770554
# #type：ype: 1 文本 ， 3 图片XML ，47 动态表情XML ， 49 文件 链接 小程序XML
# def send_quo(content,type,wxid,param):
#     return await Request.fetch("post",96,{"api":96,"content":content,"type":type,"wxid":wxid,"param":param})

# #https://www.showdoc.com.cn/wx2api/8905088612820763
# def send_forward(wxid,id=None,MsgSvrID=None):
#     if id is not None:
#         return await Request.fetch("get",10086,param1=wxid,param2=id)
#     if MsgSvrID is not None:
#         return await Request.fetch("get",10087,param1=wxid,param2=MsgSvrID)

# #https://www.showdoc.com.cn/wx2api/8905150796768180
# def send_recall(wxid,serverId=None,localId=None):
#     if serverId is not None:
#         return await Request.fetch("get",10010,param1=wxid,param2=serverId)
#     if localId is not None:
#         return await Request.fetch("get",10011,param1=wxid,param2=localId)

# #https://www.showdoc.com.cn/wx2api/8905151169084513
# def get_original_picture(xml,image,thumb=None):
#     if thumb is None:
#         return await Request.fetch("post",1033,{"api":1033,"xml":xml,"image":image})
#     else:
#         return await Request.fetch("post",1033,{"api":1033,"xml":xml,"image":image,"thumb":thumb})

# 收藏消息


# 通讯录功能
# https://www.showdoc.com.cn/wx2api/8905090079162044
class ApiReturn_wxid_details_data(BaseModel):
    userName: str
    alias: str
    nickName: str
    remark: Optional[str] = ""
    labelIDList: Optional[str] = ""
    type: int
    verifyFlag: int
    reserved2: int
    reserved5: int
    pYInitial: str
    country: str
    province: str
    city: str
    snsBgImgUrl: str
    sex: str
    signature: Optional[str] = ""
    source: int
    bigHeadImgUrl: str
    smallHeadImgUrl: str


class ApiReturn_wxid_details(ApiReturn_base):
    data: ApiReturn_wxid_details_data




async def get_wxid_details(userName):
    """
    获取个人详细信息(2101)

    获取通讯录个人详细信息，包含群成员一起
    https://www.showdoc.com.cn/wx3api/9346639244615566
    """
    return ApiReturn_wxid_details(**await Request.fetch(2101, {"userName": userName}))


class ApiReturn_bot_data(BaseModel):
    userName: str
    nickName: str
    alias: str
    mobile: str
    sex: str
    country: str
    province: str
    city: str
    signature: str
    bigHeadImgUrl: str
    smallHeadImgUrl: str



class ApiReturn_bot(ApiReturn_base):
    data: ApiReturn_bot_data



async def get_bot_details() -> ApiReturn_bot:
    return ApiReturn_bot(**await Request.fetch(2100, {}))


# 好友
# https://www.showdoc.com.cn/wx3api/9346612583048279
# TODO:
async def send_friend(userName, srcUserName):
    return ApiReturn_base(
        **await Request.fetch(2212, {"desUserName": userName, "srcUserName": srcUserName})
    )


# 群组功能
# TODO:

async def invite_member2guild(userName: str | list, chatRoomName: str):
    """邀请群成员(2306)
    https://www.showdoc.com.cn/wx3api/9346656379900403
    """

    if isinstance(userName, str):
        userName = userName.split()
    return ApiReturn_base(
        **await Request.fetch(2306, {"userName": userName, "chatRoomName": chatRoomName})
    )


# TODO:
async def kick_guild_member(userName: str | list, chatRoomName: str):
    """删除群成员(2307)
    https://www.showdoc.com.cn/wx3api/9346608044151180
    """
    """_summary_

    Args:
        userName (str | list): _description_
        chatRoomName (str): _description_

    Returns:
        _type_: _description_
    """
    if isinstance(userName, str):
        userName = userName.split()
    return ApiReturn_base(
        **await Request.fetch(2307, {"userName": userName, "chatRoomName": chatRoomName})
    )



class UpdateGuildMemberDetails_ContactList(BaseModel):
    userName: str
    nickName: str
    pyInitial: str
    quanPin: str
    remark: str
    sex: int
    signature: str
    personalCard: int
    source: int
    verifyflag: int
    alias: str
    weiboFlag: int
    snsBgImgUrl: str
    bigHeadImgUrl: str
    smallHeadImgUrl: str
    headImgMd5: str
    encryptUserName: str
    chatroomVersion: int
    chatroomMaxCount: int
    deleteFlag: int

class UpdateGuildMemberDetails_Data(BaseModel):
    errorCode: int
    errorMsg: str
    contactCount: int
    contactList: List[UpdateGuildMemberDetails_ContactList]
class UpdateGuildMemberDetails(ApiReturn_base):
    data: UpdateGuildMemberDetails_Data
async def update_guild_member_details(chatRoomName, userName):
    """更新群成员资料(2113)
    https://www.showdoc.com.cn/wx3api/9346628417456309
    """
    return UpdateGuildMemberDetails(
        **await Request.fetch(2113, {"chatRoomName": chatRoomName, "userName": userName})
    )

class GetChatroomMembersDetails_data_member(BaseModel):
    userName: str
    alias: str
    nickName: str
    encryptUserName: str
    remark: Optional[str]
    type: int
    verifyFlag: int
    reserved2: int
    reserved5: int
    pYInitial: str
    country: str
    province: Optional[str]
    city: Optional[str]
    snsBgImgUrl: str
    sex: str
    signature: str
    source: int
    bigHeadImgUrl: str
    smallHeadImgUrl: str

class GetChatroomMembersDetails_data(BaseModel):
    chatRoomName: str
    nickName: str
    master: str
    announcement: str
    announcementEditor: str
    member: List[GetChatroomMembersDetails_data_member]
    count: int

class GetChatroomMembersDetails(ApiReturn_base):
    data: GetChatroomMembersDetails_data




async def get_chatroom_members_details(chatRoomName: str):
    """获取所有群成员详细信息(2111)
    https://www.showdoc.com.cn/wx3api/9346647419679270

    """
    return GetChatroomMembersDetails(**await Request.fetch(2111, {"chatRoomName": chatRoomName}))






class ChatroomDetails_data(BaseModel):
    chatRoomName: str
    nickName: str
    remark: str
    bigHeadImgUrl: str
    smallHeadImgUrl: str
    chatRoomFlag: int
    selfDisplayName: str
    creator: str
    announcement: str
    announcementEditor: str
    announcementPublishTime: int
    member: List[str]
    count: int


class ChatroomDetails(ApiReturn_base):
    data: ChatroomDetails_data



async def get_chatroom_details(chatRoomName: str):
    """获取群详细信息(2104)
    https://www.showdoc.com.cn/wx3api/9346648196805736
    """
    return ChatroomDetails(**await Request.fetch(2104, {"chatRoomName": chatRoomName}))

class GetChatroomList_Admin(BaseModel):
    admin_id: str

class GetChatroomList_Member(BaseModel):
    member_id: str

class GetChatroomList_Record(BaseModel):
    chatRoomName: str
    creator: str
    nickName: str
    remark: Optional[str]
    chatRoomFlag: str
    selfDisplayName: str
    bigHeadImgUrl: Optional[str]
    smallHeadImgUrl: Optional[str]
    admins: List[GetChatroomList_Admin]
    member: List[GetChatroomList_Member]
    memberCount: int

class GetChatroomList_Data(BaseModel):
    page: int
    pageSize: int
    record: List[GetChatroomList_Record]


class GetChatroomList(ApiReturn_base):
    data: GetChatroomList_Data

async def get_chatroom_list(page: int = 1, pageSize: int = 100):
    """获取所有群(2110)
    https://www.showdoc.com.cn/wx3api/9346645312003486
    """

    return GetChatroomList(
        **await Request.fetch(2110, {"page": page, "pageSize": pageSize})
    )



class get_chatroom_member_Member(BaseModel):
    nickName: str
    roomNick: Optional[str]
    userName: str



class get_chatroom_member_ChatRoomData(BaseModel):
    chatRoomName: str
    nickName: str
    announcement: Optional[str]
    announcementEditor: str
    bigHeadImgUrl: Optional[str]
    smallHeadImgUrl: Optional[str]
    creator: str
    admins: List[str]
    member: List[get_chatroom_member_Member]
    count: int
class GetChatroomMember(ApiReturn_base):
    data: get_chatroom_member_ChatRoomData

async def get_chatroom_member(chatRoomName: str):
    """获取群成员(2109)
    https://www.showdoc.com.cn/wx3api/9346646985151248
    """
    return GetChatroomMember(**await Request.fetch(2109, {"chatRoomName": chatRoomName}))


# 登录
# https://www.showdoc.com.cn/wx2api/8905084291904840
class ApiReturn_LoginCheck(BaseModel):
    isLogin: bool
    self_id: str
    port: int
    pid: int



async def check_wxchat_login() -> ApiReturn_LoginCheck:
    req = await Request.fetch(2001, {})
    if req["errorCode"] == 0:
        if req["data"]["isLogin"] == 1:
            return ApiReturn_LoginCheck(
                isLogin=True,
                self_id=req["wechat"],
                port=req["port"],
                pid=req["pid"],
            )
        else:
            return ApiReturn_LoginCheck(
                isLogin=False,
                self_id="",
                port=req["port"],
                pid=req["pid"],
            )
    else:
        raise Exception("Error code: " + req["errorCode"])


# #https://www.showdoc.com.cn/wx2api/8905083174377643
# def get_QR_code_URL():
#     return await Request.fetch("get",2)

# #https://www.showdoc.com.cn/wx2api/8905083816268892
# def get_QR_code():
#     return await Request.fetch("get",3)

# #https://www.showdoc.com.cn/wx2api/8905082409027795
# def open_another_and_injection(port_another):
#     return await Request.fetch("get",31,param1=port_another)


# def get_original_picture(port,wxid,xml,image):   #测试未成功，不要用
#     apiurl=f"http://{address}:{port}"
#     data={"api": 1033,"xml":xml,"image":image}
#     res = httpx.post(apiurl , json=data)
#     print(res.text)


# def get_original_picture_2(port,wxid,xml,image):  #测试未成功，不要用
#     apiurl=f"http://{address}:{port}"
#     data={"api": 1033,"xml":xml,"image":image}
#     res = httpx.post(apiurl , json=data)
#     print(res.text)
