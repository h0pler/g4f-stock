import os
import datetime

logfile = datetime.datetime.now().strftime("logs/%y%m%d-%H:%M:%S.log")

def create_logs_directory():
    if not os.path.exists("logs"):
        os.makedirs("logs")

def log_start():
    create_logs_directory()
    with open(logfile, "a") as file:
        file.write("\n================= [LOG] =================\n")

def log_print(message: str):
    create_logs_directory()
    with open(logfile, "a") as file:
        msg = message.replace("\n", "\n  ")
        file.write("  " + msg + "\n")

def log_end():
    create_logs_directory()
    with open(logfile, "a") as file:
        file.write("\n================= [END] =================\n")
