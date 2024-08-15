from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from msg_handler import handler,ItemBase
from file_action import config_read
import logging
from logging.handlers import RotatingFileHandler
config = config_read()
connection = config.connect




app = FastAPI()


@app.post("/")
async def root(item:ItemBase):
    msgBot=handler(item)
    await msgBot.answer_old_chino()
    # await msgBot.answer_new_chino()
    return

@app.get("/upload/{file_name}")
async def upload_file(file_name: str):
    # 确保文件路径安全，这里假设所有文件都在"./files"目录下
    file_location = f"./upload/{file_name}"

    try:
        return FileResponse(path=file_location, filename=file_name)
    except Exception as e:
        # 如果发生错误，返回404
        raise HTTPException(status_code=404, detail=f"File {file_name} not found")





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=28887)
