from abc import ABC, abstractmethod


class AllowanceFunction(ABC):

    @abstractmethod
    def function(self, taxable: int) -> int:
        pass