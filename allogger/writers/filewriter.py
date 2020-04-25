import os
from time import time as timestamp
from multiprocessing import current_process

from .abstract_writer import AbstractWriter
from .helpers import gen_filename, time, add_value_wrapper
from ..helpers import _acquire_lock, _release_lock

class FileWriter(AbstractWriter):
    def __init__(self, **kwargs):
        AbstractWriter.__init__(self, **kwargs)

        self.filename = gen_filename()
        self.init_time = timestamp()

    @property
    def wall_time(self):
        return timestamp() - self.init_time

    def _run(self):
        AbstractWriter._run(self)
        self.write_to_disc()

    def write_to_disc(self):

        _acquire_lock()
        try:
            with open(os.path.join(self.output_dir, self.filename + '.log'), 'a') as f:
                for line in self.data['text']:
                    f.write(line + '\n')
        except:
            print(f'Error while writing to {os.path.join(self.output_dir, self.filename + ".log")}')
        finally:
            _release_lock()

        self.data.clear()

    def fixed_prefix(self, key):
        return f'[{key}] {time()} > '

    @add_value_wrapper
    def add_text(self, key, value):
        if 'text' not in self.data:
            self.data['text'] = self.manager.list()

        message = self.fixed_prefix(key) + value
        self.data['text'].append(message)

        return message

    @add_value_wrapper
    def add_scalar(self, key, value, step):
        pass

    @add_value_wrapper
    def add_histogram(self, key, value, step):
        pass

    @add_value_wrapper
    def add_image(self, key, value, step):
        pass

    @add_value_wrapper
    def add_scalars(self, key, value, step):
        pass

    def __repr__(self):
        return 'FileWriter'

    def close(self):
        AbstractWriter.close(self)
        if current_process().name == 'MainProcess' or self.scope != 'root':
            self.write_to_disc()
            print(f'{self} closed')

