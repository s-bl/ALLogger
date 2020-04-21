from socket import gethostname
from datetime import datetime
from time import time as timestamp

def gen_filename():
    return gethostname() + '_' + str(int(timestamp()))

def time():
    return datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

def add_value_wrapper(f):
    def wrapper(self, key, *args, **kwargs):
        if (f.__name__.split('_')[-1], key) not in self.data:
            self.data[(f.__name__.split('_')[-1], key)] = self.manager.list()

        out = f(self, key, *args, **kwargs)

        return out

    return wrapper

