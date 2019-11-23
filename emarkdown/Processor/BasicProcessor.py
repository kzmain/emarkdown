from abc import abstractmethod


class BasicProcessor:
    @property
    @abstractmethod
    def tag_name(self):
        return NotImplementedError
