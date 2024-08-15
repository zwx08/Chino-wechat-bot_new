# plugin 编写帮助

插件实现使用 pluginlib

## 定义

### 插件父类

```python
import pluginlib

@pluginlib.Parent('plugin_common', group='msg_plugin')
class plugin_common(object):

    @classmethod
    @pluginlib.abstractmethod
    def main(cls,msg_l):
        pass

@pluginlib.Parent('plugin_admin', group='msg_plugin')
class plugin_admin(object):   #有admin权限的人可用

    @classmethod
    @pluginlib.abstractmethod
    def main(cls,msg_l):
        pass
```

在收到一个消息的时候，会调用每一个插件中的 main 方法，传入 msg_l。当不为None的时候检测是AnswerBase类型还是AnswerBaseList类型，如果是其中之一则交给发送消息的部分

### msg_l 定义

```python
msg_l={"robotname":robotname,"qu":qu,"wxid":wxid,"wxid_group":wxid_group,"qu_xml":qu_xml,"qu_xml_data":qu_xml_data,"qu_reply_content":qu_reply_content,"qu_reply_wxid":qu_reply_wxid,'isChatroom': isChatroom}
```

群组中内容示例：

```json
{'robotname': '智乃', 'qu': '&ip', 'wxid': '20848218285@chatroom', 'wxid_group': 'wxid_3412raihkd6w22', 'qu_xml': None, 'qu_xml_data': None, 'qu_reply_content': None, 'qu_reply_wxid': None, 'isChatroom': True}
```

非群组中内容示例：

```json
{'robotname': '智乃', 'qu': '&ip', 'wxid': 'wxid_2eokvnwm9a5a22', 'wxid_group': '', 'qu_xml': None, 'qu_xml_data': None, 'qu_reply_content': None, 'qu_reply_wxid': None, 'isChatroom': False}
```

（qu 是消息内容）

### AnswerBase 定义

```python
class AnswerBase(BaseModel):
    answer: str | dict     # dict是直接解析到api中去的(主要是用来一些不止需要content的发送方式)，查看api_action.py
    # Replace: Optional[bool] = False
    # Replace_way: Optional[int] = 0
    send_way: Optional[Literal["Text","Image","File","Gif","Url","Xml","Quote","Fav"]] = "Text"
class AnswerBaseList(BaseModel):
    answers: List[AnswerBase]
```

Replace 说不定会删掉，别用。

## 示例插件

```python
import datetime

from Chino_old.plugins_parser import plugin_common
from Chino_old.model_definition import AnswerBase, AnswerBaseList


class TimePlugin(plugin_common):


    _version_ ='0.1'
    @classmethod
    def main(cls,msg_l) -> AnswerBase | AnswerBaseList | None:
        if msg_l["qu"].find("&getTime") != -1:

            # 获取服务器时间
            current_time = datetime.datetime.now()

            # 正确的格式化时间方式
            formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

            return AnswerBase(answer=formatted_time,send_way="Text")
    @staticmethod
    def help():
        return "&getTime to getTime"
```