from abc import ABC, abstractmethod

class AllowanceFunction(ABC):
    """Interface for classes that provide method for generating allowance from taxable amount."""
    @abstractmethod
    def function(self, taxable: int) -> int:
        pass