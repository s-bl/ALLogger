from socket import gethostname
from datetime import datetime
from time import time as timestamp

def gen_filename():
    return gethostname() + '_' + str(int(timestamp()))

def time():
    return datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

