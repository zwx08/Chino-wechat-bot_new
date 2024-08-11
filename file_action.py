import yaml
import os
from pydantic import BaseModel

class config_connect(BaseModel):
    host: str
    port: int

class config(BaseModel):
    connect: config_connect
    robotname: str

def _check_file_and_create_yaml(file_path, default_content):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            yaml.dump(default_content, file)
        raise FileNotFoundError(f"文件 {file_path} 不存在，已创建默认对象。")

# 示例文件路径和默认内容
file_path = "config.yaml"

# 创建 config 实例
default_content = config(connect=config_connect(host="127.0.0.1", port=28888),robotname="robottest").model_dump()

# 检查文件并创建默认对象
_check_file_and_create_yaml(file_path, default_content)

def config_read() -> config:
    with open('config.yaml', encoding='utf-8') as file:
        config_dict = yaml.safe_load(file)
        return config(**config_dict)