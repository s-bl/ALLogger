import os
import numpy as np
from collections import OrderedDict
from multiprocessing import current_process, Manager

from .writers import *
from .helpers import _release_lock, _acquire_lock, filter

valid_outputs = ["tensorboard", 'hdf']

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

    def __init__(self, scope, parent, **kwargs):

        self._scope = scope
        self.parent = self if scope == 'root' else parent

        self.configure(**kwargs)

    @property
    def scope(self):
        return self._scope + '-' + current_process().name.replace('-', '')

    @property
    def logdir(self):
        return self._logdir if self._logdir is not None else self.parent.logdir

    @logdir.setter
    def logdir(self, value):
        self._logdir = value

    def configure(self, logdir=None, default_outputs=None, hdf_writer_params=None, tensorboard_writer_params=None,
                  log_only_main_process=False, file_writer_params=None):

        self._logdir = logdir

        if default_outputs is not None:
            validate_outputs(default_outputs)
        self.default_outputs = default_outputs

        self.log_only_main_process = log_only_main_process

        if self._scope == 'root':
            self.manager = Manager()
            self.step_per_key = self.manager.dict()

        self.tensorboard_writer = None
        self.hdf_writer = None
        self.file_writer = None
        if logdir is not None:
            tensorboard_writer_params = tensorboard_writer_params if tensorboard_writer_params else {}
            self.tensorboard_writer = TensorboardWriter(scope=self._scope, output_dir=os.path.join(logdir, "events"),
                                                        **tensorboard_writer_params)

            hdf_writer_params = hdf_writer_params if hdf_writer_params else {}
            self.hdf_writer = HDFWriter(scope=self._scope, output_dir=os.path.join(logdir, "events"),
                                        **hdf_writer_params)

            file_writer_params = file_writer_params if file_writer_params else {}
            self.file_writer = FileWriter(scope=self._scope, output_dir=os.path.join(logdir),
                                        **file_writer_params)

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
        if self._scope != 'root':
            return self.parent.rv_step_per_key()
        else:
            return self.step_per_key

    def gen_key(self, key=None):
        scope = self.scope
        if scope.endswith('-MainProcess'):
            scope = scope[:-12]

        return scope + (('/' + key) if key else '')

    @filter
    def _to_writer(self, writer, key, data_type, data, step=None):
        if self.log_only_main_process and current_process().name != 'MainProcess':
            return

        if key is None:
            raise ValueError(f"Logging with {writer} requires a valid key")

        if step is None:
            if (self.scope, key) not in self.rv_step_per_key():
                self.rv_step_per_key()[(self.scope, key)] = 1
            step = self.rv_step_per_key()[(self.scope, key)]
            self.rv_step_per_key()[(self.scope, key)] = self.rv_step_per_key()[(self.scope, key)] + 1

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

        data_specific_writer_callable(self.gen_key(key), data, step)

        return step

    def to_hdf(self, key, data_type, data, step=None):
        return self._to_writer(self.hdf_writer or self.parent.hdf_writer, key, data_type, data, step)

    def to_tensorboard(self, key, data_type, data, step=None):
        tensorboard_writer = self.tensorboard_writer or self.parent.tensorboard_writer

        if tensorboard_writer.use_hdf_hook:
            step = self.to_hdf(key, data_type, data, step)

        return self._to_writer(tensorboard_writer or self.parent.hdf_writer, key, data_type, data, step)

    def to_stdout(self, data):
        print(data)

    def info(self, data, to_stdout=False):
        file_writer = self.file_writer if self.file_writer else self.parent.file_writer
        message = file_writer.add_text(self.gen_key(None), data)

        if to_stdout is True:
            self.to_stdout(message)

    def close(self):
        print(f'{self.scope} logger killed')
        if self.hdf_writer is not None:
            self.hdf_writer.close()
        if self.tensorboard_writer is not None:
            self.tensorboard_writer.close()
        if self.file_writer is not None:
            self.file_writer.close()

root = Logger('root', None)
manager = LoggerManager(root)

def basic_configure(*args, **kwargs):
    root.configure(*args, **kwargs)

def get_logger(scope, *args, **kwargs):
    return manager.get_logger(scope, *args, **kwargs)

def close():
    for logger in reversed(manager.logger_dict.values()):
        print(logger.scope)
        logger.close()
