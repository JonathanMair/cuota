from pydantic import BaseModel, model_validator, ValidationInfo
from typing import List, Self

from cuota.data_classes.interfaces import AllowanceFunction

class Band(BaseModel):
    """
    Represents a tax band with a defined range and payment structure.

    Attributes:
        floor (int): The lower limit of the band. Defaults to 0.
        ceiling (int): The upper limit of the band. Defaults to 200,000.
        rate (float | None): The percentage rate to apply within the band. Must be between 0 and 1.
        flat_charge (int | None): A fixed charge to apply within the band. Mutually exclusive with `rate`.
        exclusive (bool): Indicates whether only the single relevant band applies. Defaults to False.

    Methods:
        check_floor_ceiling: Validates the integrity of the band's attributes.
        get_payable: Calculates the payable amount based on an input value.
    """

    floor: int = 0
    ceiling: int = 200000
    rate: float | None = None
    flat_charge: int | None = None
    exclusive: bool = False  # if True, only payable from the single relevant band

    @model_validator(mode="after")
    def check_floor_ceiling(self) -> Self:
        """
        Validates the band's attributes for logical consistency.

        Ensures:
        - Floor and ceiling are not None.
        - Ceiling is greater than the floor.
        - Only one of `rate` or `flat_charge` is set.
        - Rate (if set) is between 0 and 1.

        Raises:
            ValueError: If any validation fails.

        Returns:
            Self: The validated Band instance.
        """
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
        """
        Calculates the payable amount based on the provided amount.

        Args:
            amount (int): The amount to calculate the payable value for.

        Returns:
            int: The payable amount.
        """
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
    """
    Represents a group of tax bands with an optional allowance.

    Attributes:
        bands (List[Band]): A list of Band instances defining the group.
        allowance (int): An amount to deduct before applying the bands. Defaults to 0.
        name (str | None): An optional name for the group.

    Methods:
        check_bands: Validates the integrity of the band's relationships.
        get_payable: Calculates the total payable amount for the group.
    """

    bands: List[Band]
    allowance: int | AllowanceFunction = 0
    name: str = None

    @model_validator(mode="after")
    def check_bands(self) -> Self:
        """
        Validates the consistency of the bands in the group.

        Ensures:
        - Allowance is non-negative.
        - The first band's floor starts at 0.
        - Each band's floor matches the ceiling of the previous band.

        Raises:
            ValueError: If any validation fails.

        Returns:
            Self: The validated BandsGroup instance.
        """
        error_msg = []
        if not isinstance(self.allowance, AllowanceFunction):
            if self.allowance < 0:
                error_msg.append("Allowance must be > 0 or class that implements the AllowanceFunction interface.")
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
        """
        Calculates the total payable amount for the group.

        Args:
            amount (int): The amount to calculate the payable value for.

        Returns:
            int: The total payable amount across all bands.
        """
        def _get_allowance(amount: int) -> int:
            if type(self.allowance) == AllowanceFunction:
                return self.allowance.function(amount)
            else:
                return self.allowance
        return int(sum([b.get_payable(amount - _get_allowance(amount)) for b in self.bands]))


class TaxModel(BaseModel):
    """
    Represents a tax model consisting of multiple bands groups.

    Attributes:
        tax_rules (List[BandsGroup]): A list of BandsGroup instances defining the rules.
        year (int): The tax year. Defaults to 2025.

    Methods:
        get_payable: Calculates the total tax payable based on the provided amount.
    """

    tax_rules: List[BandsGroup]  # TODO: make an interface to constrain these
    year: int=2025
    name: str="TaxModel"

    def get_payable(self, amount: int) -> int:
        """
        Calculates the total tax payable across all bands groups.

        Args:
            amount (int): The amount to calculate the tax for.

        Returns:
            int: The total tax payable.
        """
        payable = 0
        for r in self.tax_rules:
            r_payable = r.get_payable(amount)
            amount -= r_payable
            payable += r_payable
        return payable