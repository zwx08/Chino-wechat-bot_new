from action_sql import access, plugins_sql
from api_action import send_msg


def main(l):
    qu=l["qu"]
    if qu.find("<?xml") != 0 and qu.find("<msg>") != 0 and qu.find("//") != 0:
        send_msg.text(l["wxid"],qu)

if __name__=="__main__":
    plugins_sql.inf("repeater","0.0.1","zwx08","repeater")
    access.write("repeater","{plugin}.main",0,"复读机",Enabled="False")
