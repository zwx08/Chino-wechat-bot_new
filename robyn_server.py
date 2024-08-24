from pydantic import ValidationError
from robyn import Robyn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from msg_handler import handler,ItemBase
from file_action import config_read
import logging
from logging.handlers import RotatingFileHandler
config = config_read()
connection = config.connect

import threading
import time
from multiprocessing import Value

from robyn import Robyn, Request


app = Robyn(__file__)


@app.post("/")
async def root(request):
    try:
        item=ItemBase.model_validate_json(request.body)
    except ValidationError as e:
        print(e)
        return
    msgBot=handler(item)

    threading.Thread(target=await msgBot.answer_old_chino(), daemon=True).start()
    # await msgBot.answer_new_chino()
    return




if __name__ == "__main__":
    app.start(host="0.0.0.0", port=28887)