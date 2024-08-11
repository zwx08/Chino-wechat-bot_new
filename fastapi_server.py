from fastapi import FastAPI
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=28887)