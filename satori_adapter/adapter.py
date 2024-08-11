import asyncio
import array as arr
from typing import Any

from launart import Launart

from satori import Api, Channel, ChannelType, Event, User, Guild
from satori.model import Login, LoginStatus, MessageObject
from satori.server import Adapter, Request, route

import api_action as api



class NotLogin(RuntimeError):...




queue = asyncio.Queue()
async def get_queue():
    return queue




class Chino_adapter(Adapter):

    async def download_uploaded(self, platform: str, self_id: str, path: str) -> bytes:
        raise NotImplementedError

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"blocking"}

    def get_platform(self) -> str:
        return "ChinoWechat"
    def get_self_id(self) -> str:
        # 如果已经有 self_id，直接返回
        if self._self_id is not None:
            return self._self_id
        else:
            raise NotLogin

    # def validate_headers(self, headers: dict) -> bool:
    #     return headers["X-Platform"] == self.get_platform()

    def ensure(self, platform: str, self_id: str) -> bool:
        return platform == self.get_platform() and self_id == self.get_self_id()

    def authenticate(self, token: str) -> bool:
        return True

    async def get_logins(self):
        checkLogin=api.check_wxchat_login()
        if checkLogin.isLogin:
            self.self_id=checkLogin.self_id
            self.bot=api.get_bot_details().data
            return [Login(LoginStatus.ONLINE, user=User(self.bot.userName,self.bot.nickName,avatar=str(self.bot.snsBgImg)),self_id=self.self_id, platform="ChinoWechat")]
        else:
            raise NotLogin("Chino_wechat对接hook wechat未登录")

    async def publisher(self):
        seq = 0
        while True:
            data = await queue.get()
            match data["api"]:
                case 1005:
                    msgdata=data["data"]
                    if msgdata["isSender"]!=1:
                        msgSvrID=msgdata["msgSvrID"]
                        createtime=msgdata["createTime"]
                        channel=Channel(msgdata["userName"], ChannelType.TEXT, msgdata["nickName"])
                        if data["isChatroom"]:
                            user=User(msgdata["bytesExtra"]["userName"],msgdata["bytesExtra"]["nickName"],msgdata["bytesExtra"]["smallHeadImgUrl"])
                        else:
                            user=User(id=msgdata["userName"],name=msgdata["nickName"],avatar=msgdata["smallHeadImgUrl"])

                        match msgdata["type"]:
                            case 1:
                                yield Event(
                                    msgSvrID,
                                    "message-created",
                                    self.get_platform(),
                                    self.get_self_id(),
                                    createtime,
                                    channel=channel,
                                    user=user,
                                    message=MessageObject(f"msg_{msgSvrID}", msgdata["strContent"]),
                                )


            queue.task_done()
            seq += 1






    def __init__(self):
        super().__init__()
        self.routes = {}
        self._self_id = None
        #登录
        @self.route(Api.LOGIN_GET)
        async def on_login_get(request: Request[Any]):
            checkLogin=api.check_wxchat_login()
            if checkLogin.isLogin:
                self.self_id=checkLogin.self_id
                self.bot=api.get_bot_details().data
                return Login(LoginStatus.ONLINE, user=User(self.bot.userName,self.bot.nickName,avatar=str(self.bot.snsBgImg)),self_id=self.self_id, platform="ChinoWechat")
            else:
                raise NotLogin("Chino_wechat对接hook wechat未登录")
        #消息
        @self.route(Api.MESSAGE_CREATE)
        async def on_message_create(request: Request[route.MessageParam]):
            api.send_msg.text(request.params["channel_id"],request.params["content"])
            return [MessageObject(id="123456789", content="Hello, world!")]

        #好友
        @self.route(Api.USER_GET)
        async def on_user_get(request: Request[route.UserGetParam]):
            req=api.get_wxid_details(request.params["user_id"]).data
            return User(req.userName,req.nickName,req.alias,str(req.snsBgImgUrl))
        #群组
        @self.route(Api.GUILD_GET)
        async def on_guild_get(request: Request[route.GuildGetParam]):
            req=api.get_chatroom_details(request.params["guild_id"]).data
            return Guild(req.chatRoomName,req.nickName)

        @self.route(Api.GUILD_LIST)
        async def on_guild_list(request: Request[route.GuildListParam]):
            if "next" in request.params and (page := int(request.params["next"])):
                req=api.get_chatroom_list(page=page).data
            else:
                req=api.get_chatroom_list().data
            record=req.record
            guild_list=[]
            for i in range(len(record)):
                guild_list.append(Guild(record[i].chatRoomName,record[i].nickName))
            if int(req.total) > int(req.pageSize*page):
                return {"data": guild_list,"next": page+1}
            else:
                return {"data": guild_list}

        @self.route(Api.GUILD_MEMBER_GET)
        async def on_guild_member_get(request: Request[route.GuildMemberGetParam]):
            req=api.get_wxid_details(request.params["user_id"]).data
            user= User(req.userName,req.nickName,req.alias,str(req.snsBgImgUrl))
            if req.alias is not None:
                return GuildMember(user,req.alias)
            else:
                return GuildMember(user,req["nickName"])


        @self.route(Api.GUILD_MEMBER_LIST)
        async def on_guild_member_list(request: Request[route.GuildXXXListParam]):
            req=api.get_chatroom_members_details(request.params["guild_id"]).data
            member=req.member
            member_list=[]
            for i in range(len(member)):
                user= User(member[i].userName,member[i].nickName,member[i].alias,member[i].snsBgImgUrl)
                if member[i].alias is not None:
                    guildmember=GuildMember(user,member[i].alias)
                else:
                    guildmember=GuildMember(user,member[i].nickName)
                member_list.append(guildmember)
            return {"data": member_list}

        @self.route(Api.GUILD_MEMBER_KICK)
        async def on_guild_member_kick(request: Request[route.GuildMemberKickParam]):
            api.kick_guild_member(request.params["guild_id"],request.params["user_id"])
            return



        # #GuildRole
        # @self.route(Api.GUILD_ROLE_LIST)
        # async def on_guild_role_list(request: Request[route.GUILD_ROLE_LIST]):
        #     return {"data": [GuildRole("0","USER"),GuildRole("1","ADMIN"),GuildRole("2","OWNER")]}


        @self.route(Api.GUILD_ROLE_LIST)
        async def on_guild_role_list(request: Request[route.GuildXXXListParam]):
            return {"data": [GuildRole("0", "USER"), GuildRole("1", "ADMIN"), GuildRole("2", "OWNER")]}






    async def launch(self, manager: Launart):
        async with self.stage("blocking"):
            await manager.status.wait_for_sigexit()




