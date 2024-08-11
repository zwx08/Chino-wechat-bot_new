import logging
# time_out=time.strftime("%H:%M:%S", time.localtime())
# def standard_print(pri_content):
    # print(f"[{time_out}]{pri_content}")

def printmsg_send(userName,content):
    logging.info(f"[msg_send] {userName} << {content}")
def printmsg_rece(content):
    logging.info(f"[msg_rece] {content}")
def printerr(content):
    logging.error(f"[Error] {content}")
def printinf(content):
    logging.info(f"[info] {content}")
def printres(content):
    logging.debug(f"[Response] {content}")
