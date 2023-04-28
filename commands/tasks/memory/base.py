import abc

class MemoryProviderSingleton(abc.ABC):
    @abc.abstractmethod
    def add(self, data):
        pass

    @abc.abstractmethod
    def get(self, data):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def get_relevant(self, text: str, k: int):
        pass

    @abc.abstractmethod
    def get_stats(self):
        pass
