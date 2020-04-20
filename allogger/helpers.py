from threading import RLock
from re import search as re_search

def step_per_key_init_func():
    return 1

_lock = RLock()

def _acquire_lock():
    _lock.acquire()

def _release_lock():
    _lock.release()

def filter(f):
    def wrapper(self, writer, key, *args, **kwargs):
        if re_search(writer.filter, key) is None:
            print(f'{writer} ignoring {key}')
            return

        return f(self, writer, key, *args, **kwargs)

    return wrapper