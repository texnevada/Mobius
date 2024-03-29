import logging
import configparser
import datetime
import threading
import queue
from data.functions.MySQL_Connector import MyDB
config = configparser.ConfigParser()
config.read("./config.ini")


def get_log(name: str):
    logger = logging.Logger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | [%(levelname)s] | %(name)s: %(message)s')
    stream_formatter = logging.Formatter('%(message)s')

    if config["Logging"]["logs"].lower() == "true":
        # now = datetime.datetime.now()
        # time = now.strftime("%d.%m.%y")
        log_file = config["Logging"]["Log_location"]
        bot_name = config["APP"]["Bot_Name"]
        file_handler = logging.FileHandler(f"{log_file}/{bot_name}_runtime.log", encoding="utf-8", mode='w')
        file_handler.setLevel(int(config["Logging"]["file_log_Type"]))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)
    logger.setLevel(int(config["Logging"]["console_log_type"]))
    logger.addHandler(stream_handler)

    if config["Databases"]["Log_to_MySQL"].lower() == "true":
        mysql_handler = MySQLHandler()
        logger.addHandler(mysql_handler)
        threading.Thread(target=process_logs, args=(mysql_handler.log_queue,), daemon=True).start()

    return logger


class MySQLHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.log_queue = queue.Queue()

    def emit(self, record):
        self.log_queue.put(record)


def process_logs(log_queue):
    c = MyDB("Logging")
    while True:
        try:
            record = log_queue.get(timeout=1)
            level = record.levelname
            msg = record.getMessage()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cog_name = record.name
            sql = (f"INSERT INTO {config['Databases']['Logging_Table']} (datetime, severity, cog_name, message) "
                   f"VALUES (%s, %s, %s, %s)")
            values = (now, level, cog_name, msg)
            c.execute(sql, values)
            c.commit()
        except queue.Empty:
            continue
    c.close()

