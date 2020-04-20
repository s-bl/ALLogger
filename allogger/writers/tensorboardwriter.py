from tensorboardX import SummaryWriter

from .abstract_writer import AbstractWriter

class TensorboardWriter(AbstractWriter):
    def __init__(self, output_dir, use_hdf_hook=True, filter='.*'):
        super().__init__(filter=filter)

        self.output_dir = output_dir
        self.summary_writer = SummaryWriter(output_dir)
        self.use_hdf_hook = use_hdf_hook

    def add_scalar(self, key, value, step):
        self.summary_writer.add_scalar(key, value, step)

    def add_histogram(self, key, value, step):
        self.summary_writer.add_histogram(key, value, step)

    def add_image(self, key, value, step):
        self.summary_writer.add_image(key, value, step)

    def add_scalars(self, key, value, step):
        self.summary_writer.add_scalars(key, value, step)

    def __repr__(self):
        return 'TensorboardWriter'

    def __del__(self):
        print('killed TensorboardWriter')

