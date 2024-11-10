from pydantic import BaseModel, model_validator, ValidationInfo
from typing import List, Self
import logging

logger = logging.getLogger()


class Band(BaseModel):
    """
    A band in a tax rule, with floor, ceiling and EITHER rate (0<rate<=1) or a flat_charge to apply to the interval
    between floor and ceiling.
    """
    floor: int
    ceiling: int
    rate: float | None = None
    flat_charge: int | None = None

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
        if amount < self.floor:
            interval = 0
        elif amount > self.ceiling:
            interval = self.ceiling - self.floor
        else:
            interval = amount - self.floor
        return interval * self.rate if self.rate is not None else self.flat_charge


class BandsGroup(BaseModel):
    bands: List[Band]
    year: int = 2024
    allowance: int = 0

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

    def get_payable(self, amount: int) -> int:
        payable = 0
        for r in self.tax_rules:
            r_payable = r.get_payable(amount)
            amount -= r_payable
            payable += r_payable
        return payable
