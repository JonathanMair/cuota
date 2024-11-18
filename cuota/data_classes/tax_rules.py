from pydantic import BaseModel, model_validator, ValidationInfo
from typing import List, Self
import logging

logger = logging.getLogger()


class Band(BaseModel):
    floor: int = 0
    ceiling: int = 200000
    rate: float | None = None
    flat_charge: int | None = None
    exclusive: bool=False  # if True only get payable from the single relevant band

    @model_validator(mode="after")
    def check_floor_ceiling(self) -> Self:
        error_msg = []
        if self.floor is None:
            error_msg.append("Floor must not be None.")
        if self.ceiling is None:
            error_msg.append("Ceiling must not be None.")
        if self.ceiling <= self.floor:
            error_msg.append("Ceiling must be greater than floor.")
        if len(error_msg) > 0:
            error_msg.append("Floor must be smaller than ceiling")
        if self.rate is not None and self.flat_charge is not None:
            error_msg.append("Only flat_charge or rate must be set, not both.")
        if self.rate is None and self.flat_charge is None:
            error_msg.append("Either flat_charge or rate must be set.")
        if self.rate is not None and (self.rate > 1 or self.rate < 0):
            error_msg.append("Rate must be greater than or equal to 0 or less than or equal to 1.")
        if len(error_msg) > 0:
            error_msg_joined = "\n" + "\n".join(error_msg)
            raise ValueError(f"{error_msg_joined}")
        return self

    def get_payable(self, amount: int) -> int:
        if self.rate is None:
            if self.ceiling >= amount > self.floor:
                return self.flat_charge
            else:
                return 0
        if self.exclusive:
            if self.ceiling >= amount > self.floor:
                return int(self.rate * amount)
            else:
                return 0
        else:  # this is a non-exclusive % band
            if amount < self.floor:  # amount is below this band, nothing due
                return 0
            elif amount > self.ceiling:  # amount is above ceiling, apply % to whole band
                return int((self.ceiling - self.floor) * self.rate)
            else:  # amount falls within the band, apply rate proportionally
                return int((amount - self.floor) * self.rate)


class BandsGroup(BaseModel):
    bands: List[Band]
    allowance: int=0
    name: str=None

    @model_validator(mode="after")
    def check_bands(self) -> Self:
        error_msg = []
        if self.allowance < 0:
            error_msg.append("Allowance must be > 0.")
        b = self.bands
        if b[0].floor != 0:
            error_msg.append("Floor of first band must == 0")
        for i in range(1, len(b)):  # check bands except first
            if b[i].floor != b[i - 1].ceiling:  # band floor must == ceiling of previous band
                error_msg.append(f"band floor [{b[i].floor}] does not match ceiling of previous band.")
        if len(error_msg) > 0:
            error_msg_joined = "\n" + "\n".join(error_msg)
            raise ValueError(f"{error_msg_joined}")
        return self

    def get_payable(self, amount: int) -> int:
        return int(sum([b.get_payable(amount - self.allowance) for b in self.bands]))


class TaxModel(BaseModel):
    tax_rules: List[BandsGroup]  # TODO: make an interface to constrain these
    year: int = 2025

    def get_payable(self, amount: int) -> int:
        payable = 0
        for r in self.tax_rules:
            r_payable = r.get_payable(amount)
            amount -= r_payable
            payable += r_payable
        return payable


