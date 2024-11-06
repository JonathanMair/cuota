from pydantic import BaseModel
from typing import Iterable


class Band(BaseModel):
    floor: int
    ceiling: int
    rate: float

    def get_payable(self, amount: int) -> int:
        if amount < self.floor:
            return 0
        if amount > self.ceiling:
            return (self.ceiling - self.floor) * self.rate
        return int((amount - self.floor) * self.rate)


class Bands(BaseModel):
    bands: Iterable[Band]
