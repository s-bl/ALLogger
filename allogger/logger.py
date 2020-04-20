import os
import numpy as np
from collections import defaultdict, OrderedDict

from .writers import *
from .helpers import _release_lock, _acquire_lock, step_per_key_init_func, filter

valid_outputs = ["tensorboard", "stdout", 'hdf']

def validate_outputs(outputs):
    for d in outputs:
        if d not in valid_outputs:
            raise ValueError(f"{d} is not a valid output")

class LoggerManager():

    def __init__(self, root):
        self.root = root
        self.logger_dict = OrderedDict()
        self.logger_dict['root'] = self.root

    def get_logger(self, scope, *args, **kwargs):

        if scope.split('.')[0] != 'root':
            scope = 'root.' + scope

        _acquire_lock()
        try:
            if scope in self.logger_dict:
                return self.logger_dict[scope]
            else:
                parent = self._get_parent(scope)
                self.logger_dict[scope] = Logger(scope, parent, *args, **kwargs)
                return self.logger_dict[scope]
        finally:
            _release_lock()

    def _get_parent(self, scope):
        parent_scope = scope[:scope.rfind('.')]
        while True:
            if parent_scope in self.logger_dict:
                break
            parent_scope = parent_scope[:parent_scope.rfind('.')]
        return self.logger_dict[parent_scope]

class Logger:

    def __init__(self, scope, parent, logdir=None, default_outputs=None, hdf_writer_params=None, tensorboard_writer_params=None):

        self.scope = scope
        self.parent = self if scope == 'root' else parent

        self.configure(logdir, default_outputs, hdf_writer_params, tensorboard_writer_params)

    def configure(self, logdir, default_outputs, hdf_writer_params=None, tensorboard_writer_params=None):
        self.logdir = logdir

        if default_outputs is not None:
            validate_outputs(default_outputs)
        self.default_outputs = default_outputs

        if self.scope == 'root':
            self.step_per_key = defaultdict(step_per_key_init_func)

        self.tensorboard_writer = None
        self.hdf_writer = None
        if logdir is not None:
            tensorboard_writer_params = tensorboard_writer_params if tensorboard_writer_params is not None else {}
            self.tensorboard_writer = TensorboardWriter(os.path.join(logdir, "events"), **tensorboard_writer_params)

            hdf_writer_params = hdf_writer_params if hdf_writer_params is not None else {}
            self.hdf_writer = HDFWriter(os.path.join(logdir, "events"), **hdf_writer_params)

    def infer_datatype(self, data):
        if np.isscalar(data):
            return "scalar"
        elif isinstance(data, np.ndarray):
            if data.ndim == 0:
                return "scalar"
            elif data.ndim == 1:
                if data.size == 1:
                    return "scalar"
                if data.size > 1:
                    return "histogram"
            elif data.ndim == 2:
                return "image"
            else:
                raise NotImplementedError("Numpy arrays with more than 2 dimensions are not supported")
        else:
            raise NotImplementedError(f"Data type {type(data)} not understood.")

    def log(self, data, key=None, data_type=None, to_tensorboard=None, to_stdout=None, to_csv=None, to_hdf=None):
        if data_type is None:
            data_type = self.infer_datatype(data)

        default_outputs = self.default_outputs or self.parent.default_outputs

        output_callables = []
        if to_tensorboard or (to_tensorboard is None and 'tensorboard' in default_outputs):
            output_callables.append(self.to_tensorboard)
        if to_stdout or (to_stdout is None and 'stdout' in default_outputs):
            output_callables.append(self.to_stdout)
        if to_csv or (to_csv is None and 'csv' in default_outputs):
            raise NotImplementedError('CSV writer not implemented')
            # output_callables.append(self.to_csv)
        if to_hdf or (to_hdf is None and 'hdf' in default_outputs):
            output_callables.append(self.to_hdf)

        for output_callable in output_callables:
            output_callable(key, data_type, data)

    def rv_step_per_key(self):
        if self.scope != 'root':
            return self.parent.rv_step_per_key()
        else:
            return self.step_per_key

    @filter
    def _to_writer(self, writer, key, data_type, data, step=None):
        if key is None:
            raise ValueError(f"Logging with {writer} requires a valid key")

        if step is None:
            step = self.rv_step_per_key()[(self.scope, key)]
            self.rv_step_per_key()[(self.scope, key)] += 1

        if data_type == "scalar":
            data_specific_writer_callable = writer.add_scalar
        elif data_type == "histogram":
            data_specific_writer_callable = writer.add_histogram
        elif data_type == "image":
            data_specific_writer_callable = writer.add_image
        elif data_type == 'scalars':
            data_specific_writer_callable = writer.add_scalars
        else:
            raise NotImplementedError(f"{writer} does not support type {data_type}")

        data_specific_writer_callable(self.scope + "/" + key, data, step)

        return step

    def to_hdf(self, key, data_type, data, step=None):
        return self._to_writer(self.hdf_writer or self.parent.hdf_writer, key, data_type, data, step)

    def to_tensorboard(self, key, data_type, data, step=None):
        tensorboard_writer = self.tensorboard_writer or self.parent.tensorboard_writer

        if tensorboard_writer.use_hdf_hook:
            step = self.to_hdf(key, data_type, data, step)

        return self._to_writer(tensorboard_writer or self.parent.hdf_writer, key, data_type, data, step)

    def to_stdout(self, key, data_type, data):
        if not data_type == "scalar":
            raise NotImplementedError("Only data type 'scalar' supported for stdout output")

        print(f"[{self.scope}] {key}: {data}")

    def close(self):
        print(f'{self.scope} logger killed')
        if self.hdf_writer is not None:
            self.hdf_writer.close()
        if self.tensorboard_writer is not None:
            self.tensorboard_writer.close()

root = Logger('root', None)
manager = LoggerManager(root)

def basic_configure(logdir, default_outputs, hdf_writer_params=None, tensorboard_writer_params=None):
    root.configure(logdir, default_outputs, hdf_writer_params, tensorboard_writer_params)

def get_logger(scope, *args, **kwargs):
    return manager.get_logger(scope, *args, **kwargs)

def close():
    for logger in reversed(manager.logger_dict.values()):
        print(logger.scope)
        manager.logger_dict[logger.scope] = None
        logger.close()
