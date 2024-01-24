import datetime

logfile = datetime.datetime.now().strftime("logs/%y%m%d-%H:%M:%S.log")


def log_start():
    with open(logfile, "a") as file:
        file.write("\n\n================= [LOG] =================\n")


def log_print(prefix, message):
    with open(logfile, "a") as file:
        file.write(prefix + "  " + message + "\n")


def log_end():
    with open(logfile, "a") as file:
        file.write("\n================= [END] =================\n")
