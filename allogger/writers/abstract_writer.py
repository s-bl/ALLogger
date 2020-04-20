from abc import ABC, abstractmethod
from time import time as timestamp

from .helpers import time

class AbstractWriter(ABC):

    def __init__(self, filter='.*'):
        self.init_time = timestamp()
        self.last_write_time = self.init_time
        self.filter = filter

    @property
    def wall_time(self):
        return timestamp() - self.init_time

    @property
    def time_diff_from_last_write(self):
        return timestamp() - self.last_write_time

    @abstractmethod
    def add_scalar(self, key, value, step):
        raise NotImplementedError

    @abstractmethod
    def add_histogram(self, key, value, step):
        raise NotImplementedError

    @abstractmethod
    def add_image(self, key, value, step):
        raise NotImplementedError

    @abstractmethod
    def add_scalars(self, key, value, step):
        raise NotImplementedError

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError
