import os
import pandas as pd
from time import time as timestamp

from .abstract_writer import AbstractWriter
from .helpers import gen_filename, time
from ..helpers import _acquire_lock, _release_lock

def add_value_wrapper(f):
    def wrapper(self, key, *args, **kwargs):
        if (f.__name__.split('_')[-1], key) not in self.data:
            self.data[(f.__name__.split('_')[-1], key)] = []

        out = f(self, key, *args, **kwargs)

        self.write_to_disc()

        return out

    return wrapper

class HDFWriter(AbstractWriter):
    def __init__(self, output_dir, min_time_diff_btw_disc_writes=180, filter='.*'):
        super().__init__(filter=filter)

        self.output_dir = output_dir
        self.data = dict()
        self.min_time_diff_btw_disc_writes = min_time_diff_btw_disc_writes
        self.filename = gen_filename()
        self.init_time = timestamp()
        self.last_write_time = self.init_time

    @property
    def wall_time(self):
        return timestamp() - self.init_time

    @property
    def time_diff_from_last_write(self):
        return timestamp() - self.last_write_time

    def write_to_disc(self, force=False):
        if (timestamp() - self.last_write_time) < self.min_time_diff_btw_disc_writes and not force:
            return

        for (type, k), v in self.data.items():
            data = pd.DataFrame(v, columns=['step', 'time', 'wall_time', 'value']).set_index('step')
            _acquire_lock()
            try:
                data.to_hdf(os.path.join(self.output_dir, self.filename + '.h5'), key=type + '/' + k.split('.')[-1], append=True, format='table')
            except:
                print(f'Error while writing to {os.path.join(self.output_dir, self.filename + ".h5")}')
            finally:
                _release_lock()
        self.data = dict()

        self.last_write_time = timestamp()

    def fixed_data_prefix(self, step):
        return [step, time(), self.wall_time]

    @add_value_wrapper
    def add_scalar(self, key, value, step):
        self.data[('scalar', key)].append(self.fixed_data_prefix(step) + [value])

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
        return 'HDFWriter'

    def close(self):
        self.write_to_disc(force=True)

