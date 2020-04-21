import os
import pandas as pd
from time import time as timestamp
from multiprocessing import current_process

from .abstract_writer import AbstractWriter
from .helpers import gen_filename, time, add_value_wrapper
from ..helpers import _acquire_lock, _release_lock

class HDFWriter(AbstractWriter):
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

        for (type, k), v in self.data.items():
            data = pd.DataFrame(list(v), columns=['step', 'time', 'wall_time', 'value']).set_index('step')
            _acquire_lock()
            try:
                data.to_hdf(os.path.join(self.output_dir, self.filename + '.h5'), key=type + '/' + k.split('.')[-1].replace('-', '/'), append=True, format='table')
            except:
                print(f'Error while writing to {os.path.join(self.output_dir, self.filename + ".h5")}')
            finally:
                _release_lock()

        self.data.clear()

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
        AbstractWriter.close(self)
        if current_process().name == 'MainProcess' or self.scope != 'root':
            self.write_to_disc()
            print(f'{self} closed')

