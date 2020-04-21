from tensorboardX import SummaryWriter
from multiprocessing import current_process

from .abstract_writer import AbstractWriter
from .helpers import add_value_wrapper
from ..helpers import _acquire_lock, _release_lock

class TensorboardWriter(AbstractWriter):
    def __init__(self, use_hdf_hook=True, **kwargs):

        AbstractWriter.__init__(self, **kwargs)

        self.use_hdf_hook = use_hdf_hook

        if current_process().name == 'MainProcess' or self.scope != 'root':
            self.summary_writer = SummaryWriter(self.output_dir)

    def _run(self):
        AbstractWriter._run(self)
        self.write_to_writer()

    def write_to_writer(self):
        for (type, k), v in self.data.items():
            for (step, value) in list(v):
                _acquire_lock()
                try:
                    if type == 'scalar':
                        self.summary_writer.add_scalar(k, step, value)
                    elif type == 'histogram':
                        self.summary_writer.add_histogram(k, step, value)
                    elif type == 'image':
                        self.summary_writer.add_image(k, step, value)
                    elif type == 'scalars':
                        self.summary_writer.add_scalars(k, step, value)
                finally:
                    _release_lock()

        self.data.clear()

    def add_data(self, type, key, value, step):
        self.data[(type, key)].append([step, value])

    @add_value_wrapper
    def add_scalar(self, key, value, step):
        self.add_data('scalar', key, value, step)

    @add_value_wrapper
    def add_histogram(self, key, value, step):
        self.add_data('histogram', key, value, step)

    @add_value_wrapper
    def add_image(self, key, value, step):
        self.add_data('image', key, value, step)

    @add_value_wrapper
    def add_scalars(self, key, value, step):
        self.add_data('scalars', key, value, step)

    def __repr__(self):
        return 'TensorboardWriter'

    def close(self):
        AbstractWriter.close(self)
        if current_process().name == 'MainProcess' or self.scope != 'root':
            self.write_to_writer()
            self.summary_writer.close()
            print(f'{self} closed')
