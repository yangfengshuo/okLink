import csv
import datetime
import os
import threading
from logging import Logger

try:
    os.mkdir('log')
except:
    pass

class Logger:
    def __init__(self):
        self.fp = open(f"log/{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.csv,",'wa',newline='',encoding='utf-8')
        self.csv_writer = csv.writer(self.fp)
        self.logger_lock = threading.Lock()

    def writer_logger(self,location,err):
        with self.logger_lock:
            self.print_log(location=location,err=err)
            self.csv_writer.writerow([
                "Time: ",
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+" / ",
                "Location: "+" / ",
                location,
                "Error: "+" / ",
                err
            ])
            self.fp.flush()

    def print_log(self,location,err):
        format = f'time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | location: <{location}> | error: {err}'
        print(format)

    def info(self, msg: str) -> None:
        format = f'time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | msg: '
        print(format, msg)

