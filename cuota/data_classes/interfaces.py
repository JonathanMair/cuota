from abc import ABC, abstractmethod
from pydantic import BaseModel

class AllowanceFunction(ABC, BaseModel):
    """Interface for classes that provide method for generating allowance from taxable amount."""
    @abstractmethod
    def function(self, taxable: int) -> int:
        pass