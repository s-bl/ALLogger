from abc import ABC, abstractmethod

class AbstractWriter(ABC):

    def __init__(self, filter='.*'):
        self.filter = filter

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

    @abstractmethod
    def close(self):
        raise NotImplementedError
