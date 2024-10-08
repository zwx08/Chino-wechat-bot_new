import httpx,ujson
from action_sql import plugins_sql, qu_key
from api_action import send_art, send_msg


def main(l):
    name=l["qu"][7:]
    wxid=l["wxid"]
    req_json=httpx.post('https://api.xingzhige.com/API/NetEase_CloudMusic/',data={"name":name,"n":1})
    print(req_json.text)
    req=ujson.loads(req_json.text)
    if req["code"] == 0:
        req_data=req["data"]
        send_art(req_data["name"],wxid,req_data["cover"],req_data["songname"],req_data["songurl"])
        if req_data["pay"]=="免费":
            send_msg.text(wxid,req_data["src"])
        if req_data["pay"]=="VIP":
            re=f"http://tool.liumingye.cn/music/?page=audioPage&type=YQB&name={name}"
            send_msg.text(wxid,re)
    else:
            return f'{req.get("code")} {req.get("msg")}'

if __name__=="__main__":
    plugins_sql.inf("music_wangyi",0.01,"zwx08","网易云点歌")
    qu_key.write("music_wy","&music",1,"{plugin}.main",1)
