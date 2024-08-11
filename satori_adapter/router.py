from satori import MessageObject
from satori import Channel, ChannelType, Event, User, Guild, GuildMember
from satori.const import Api
from satori.model import Login, LoginStatus
from satori.server import Request, RouterMixin, route
import api_action as api
import array as arr

class NotLogin(RuntimeError):...
class Chino_router(RouterMixin):
    def __init__(self):
        self.routes = {}
        #登录
        @self.route(Api.LOGIN_GET)
        async def on_login_get(request):
            checkLogin=api.check_wxchat_login()
            if checkLogin["isLogin"]:
                self.self_id=checkLogin["self_id"]
                return Login(LoginStatus.ONLINE, self.self_id, platform="ChinoWechat",features=arr.array('u', ["guild.plain", "user.get", "cherry"]))
            else:
                raise NotLogin("Chino_wechat对接hook wechat未登录")
        #消息
        #消息
        @self.route(Api.MESSAGE_CREATE)
        async def on_message_create(request: Request[route.MessageParam]):
            api.send_msg.text(request.channel_id, request.content)
            return [MessageObject(id="123456789", content="Hello, world!")]

        #好友
        @self.route(Api.USER_GET)
        async def on_user_get(request: Request[route.USER_GET]):
            req=api.get_wxid_details(request["user_id"]).data()
            return User(req["userName"],req["nickName"],req["alias"],req["snsBgImgUrl"])
        #群组
        @self.route(Api.GUILD_GET)
        async def on_guild_get(request: Request[route.GUILD_GET]):
            req=api.GetChatroomDetails(request["guild_id"]).data()
            return [Guild(req["chatRoomName"],req["nickName"])]

        @self.route(Api.GUILD_LIST)
        async def on_guild_list(request: Request[route.GUILD_LIST]):
            page=Request["next"]
            if page is not None:
                req=api.get_chatroom_list(page=page).data()
            else:
                req=api.get_chatroom_list().data()
            record=req["record"]
            guild_list=[]
            for i in range(len(record)):
                guild_list.append(Guild(record[i]["chatRoomName"],record[i]["nickName"]))
            if req["total"] > req["pageSize"]*page:
                return [{"data": guild_list,"next": page+1}]
            else:
                return [{"data": guild_list}]

        @self.route(Api.GUILD_MEMBER_GET)
        async def on_guild_member_get(request: Request[route.GUILD_MEMBER_GET]):
            req=api.get_wxid_details(request["user_id"]).data()
            user= User(req["userName"],req["nickName"],req["alias"],req["snsBgImgUrl"])
            if req["alias"] is not None:
                return GuildMember(user,req["alias"])
            else:
                return GuildMember(user,req["nickName"])


        @self.route(Api.GUILD_MEMBER_LIST)
        async def on_guild_member_list(request: Request[route.GUILD_MEMBER_LIST]):
            page=Request["next"]
            if page is not None:
                req=api.get_chatroom_members_details(request["guild_id"],page=page).data()
            else:
                req=api.get_chatroom_members_details(request["guild_id"]).data()
            member=req["member"]
            member_list=[]
            for i in range(len(member)):
                user= User(member[i]["userName"],member[i]["nickName"],member[i]["alias"],member[i]["snsBgImgUrl"])
                if member[i]["alias"] is not None:
                    guildmember=GuildMember(user,member[i]["alias"])
                else:
                    guildmember=GuildMember(user,member[i]["nickName"])
                member_list.append(guildmember)

            if req["total"] > req["pageSize"]*page:
                return [{"data": member_list,"next": page+1}]
            else:
                return [{"data": member_list}]

        @self.route(Api.GUILD_MEMBER_KICK)
        async def on_guild_member_kick(request: Request[route.GUILD_MEMBER_KICK]):
            api.kick_guild_member(request["guild_id"],request["user_id"])
            return



        #GuildRole
        @self.route(Api.GUILD_ROLE_LIST)
        async def on_guild_role_list(request: Request[route.GUILD_ROLE_LIST]):
            return

