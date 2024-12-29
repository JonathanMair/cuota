import matplotlib.pyplot as plt
from pydantic import BaseModel, model_validator, ConfigDict
from typing import List, Self, Dict
import pandas as pd
import numpy as np

from cuota.data_classes.interfaces import AllowanceFunction


class Band(BaseModel):
    """
    Represents a tax band with a defined range and payment structure.

    Attributes:
        floor (int): The lower limit of the band. Defaults to 0.
        ceiling (int): The upper limit of the band. Defaults to 200,000.
        rate (float | None): The percentage rate applied to amounts within the band. Must be between 0 and 1.
        flat_charge (int | None): A fixed charge applied to the band. Mutually exclusive with `rate`.
        exclusive (bool): If True, only the single relevant band applies. Defaults to False.

    Methods:
        check_floor_ceiling() -> Self:
            Validates the integrity of the band's attributes, such as logical consistency and exclusive constraints.

        get_payable(amount: int) -> int:
            Calculates the payable amount for a given input value within the band.

        convert(rate: float):
            Adjusts the band's floor, ceiling, and flat charge by a given rate.
    """

    floor: int = 0
    ceiling: int = 200000
    rate: float | None = None
    flat_charge: int | None = None
    exclusive: bool = False
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def check_floor_ceiling(self) -> Self:
        """
        Validates the band's attributes for logical consistency.

        Ensures:
        - `floor` and `ceiling` are not None.
        - `ceiling` is greater than `floor`.
        - Only one of `rate` or `flat_charge` is defined.
        - `rate` (if defined) is between 0 and 1.

        Raises:
            ValueError: If any of these validations fail.

        Returns:
            Self: The validated `Band` instance.
        """
        error_msg = []
        if self.ceiling <= self.floor:
            error_msg.append("Ceiling must be greater than floor.")
        if self.rate is not None and self.flat_charge is not None:
            error_msg.append("Only one of flat_charge or rate must be set, not both.")
        if self.rate is None and self.flat_charge is None:
            error_msg.append("Either flat_charge or rate must be set.")
        if self.rate is not None and not (0 <= self.rate <= 1):
            error_msg.append("Rate must be between 0 and 1.")
        if error_msg:
            raise ValueError("\n".join(error_msg))
        return self

    def get_payable(self, amount: int) -> int:
        """
        Calculates the payable amount based on the provided value.

        Args:
            amount (int): The amount to calculate the payable value for.

        Returns:
            int: The payable amount, considering the band's rate or flat charge.
        """
        if self.rate is None:
            return self.flat_charge if self.ceiling >= amount > self.floor else 0
        if self.exclusive:
            return int(self.rate * amount) if self.ceiling >= amount > self.floor else 0
        if amount < self.floor:
            return 0
        if amount > self.ceiling:
            return int((self.ceiling - self.floor) * self.rate)
        return int((amount - self.floor) * self.rate)

    def convert(self, rate: float):
        """
        Adjusts the band's floor, ceiling, and flat charge by a given rate.

        Args:
            rate (float): The conversion rate to scale the band's attributes.
        """
        self.floor = int(self.floor * rate)
        self.ceiling = int(self.ceiling * rate)
        if self.flat_charge is not None:
            self.flat_charge = int(self.flat_charge * rate)


class BandsGroup(BaseModel):
    """
    Represents a group of tax bands with an optional allowance.

    Attributes:
        bands (List[Band]): A list of `Band` instances defining the group.
        allowance (int | AllowanceFunction): A deduction applied before evaluating the bands.
        name (str | None): An optional name for the group.

    Methods:
        check_bands() -> Self:
            Validates the relationships and constraints among the group's bands.

        get_payable(amount: int) -> int:
            Calculates the total payable amount for the group based on the input value.

        convert(rate: float):
            Adjusts all bands in the group by the given rate.
    """

    bands: List[Band]
    allowance: int | AllowanceFunction = 0
    name: str = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def check_bands(self) -> Self:
        """
        Validates the consistency of the bands within the group.

        Ensures:
        - `allowance` is non-negative.
        - The first band's floor is 0.
        - Each band's floor matches the ceiling of the previous band.

        Raises:
            ValueError: If any of these validations fail.

        Returns:
            Self: The validated `BandsGroup` instance.
        """
        error_msg = []
        if not isinstance(self.allowance, AllowanceFunction) and self.allowance < 0:
            error_msg.append("Allowance must be non-negative or implement AllowanceFunction.")
        if self.bands[0].floor != 0:
            error_msg.append("The floor of the first band must be 0.")
        for i in range(1, len(self.bands)):
            if self.bands[i].floor != self.bands[i - 1].ceiling:
                error_msg.append(f"Band {i} floor does not match the ceiling of the previous band.")
        if error_msg:
            raise ValueError("\n".join(error_msg))
        return self

    def get_payable(self, amount: int) -> int:
        """
        Calculates the total payable amount for the group.

        Args:
            amount (int): The amount to calculate the payable value for.

        Returns:
            int: The total payable amount across all bands, adjusted for the allowance.
        """
        allowance = self.allowance.function(amount) if isinstance(self.allowance, AllowanceFunction) else self.allowance
        return sum(b.get_payable(amount - allowance) for b in self.bands)

    def convert(self, rate: float):
        """
        Adjusts all bands in the group by the given rate.

        Args:
            rate (float): The conversion rate to scale the group's attributes.
        """
        for band in self.bands:
            band.convert(rate)


class TaxModel(BaseModel):
    """
    Represents a tax model consisting of multiple bands groups.

    Attributes:
        tax_rules (List[BandsGroup]): A list of `BandsGroup` instances defining the rules.
        year (int): The tax year. Defaults to 2025.
        name (str): The name of the tax model. Defaults to "TaxModel".
        non_sequential (bool): If True, applies each band's rules independently.

    Methods:
        results(amount: int) -> Dict:
            Calculates the detailed tax results, including payable amounts, total, and effective rate.

        marginal_rate(amount: int, delta: int = 100) -> float:
            Calculates the marginal tax rate for a given amount and delta.

        sample(taxable_array: np.array) -> pd.DataFrame:
            Generates a DataFrame summarizing tax calculations for a range of amounts.

        convert(rate: float):
            Adjusts all groups in the tax model by a given rate.
    """
    tax_rules: List[BandsGroup]
    year: int = 2025
    name: str = "TaxModel"
    non_sequential: bool = False

    def results(self, amount: int) -> Dict:
        """
        Calculates the detailed tax results for a given amount.

        Args:
            amount (int): The taxable amount.

        Returns:
            Dict: A dictionary containing individual payable amounts, total payable, take-home amount, and effective rate.
        """
        result = {}
        taxable = amount
        total = 0
        for rule in self.tax_rules:
            payable = rule.get_payable(taxable)
            result[rule.name] = payable
            if not self.non_sequential:
                taxable -= payable
            total += payable
        result.update({
            "total payable": total,
            "take home": amount - total,
            "effective rate": total / amount if amount > 0 else 0,
        })
        return result

    def marginal_rate(self, amount: int, delta: int = 100) -> float:
        """
        Calculates the marginal tax rate for a given amount and delta.

        Args:
            amount (int): The base taxable amount.
            delta (int): The incremental change in the taxable amount. Defaults to 100.

        Returns:
            float: The marginal tax rate.
        """
        r1 = self.results(amount)["total payable"]
        r2 = self.results(amount + delta)["total payable"]
        return (r2 - r1) / delta

    def sample(self, taxable_array: List[int] | None=None, income_range: tuple | None=None) -> pd.DataFrame:
        """
        Generates a DataFrame summarizing tax calculations for a range of amounts.

        Args:
            taxable_array (np.array): Array of taxable amounts to evaluate.

        Returns:
            pd.DataFrame: A DataFrame with calculated results for each taxable amount,
                          including marginal rates.
        """
        if (taxable_array is None) and (income_range is None):
            try:
                taxable_array = range(12000, 60000, 100)
            except:
                raise ValueError()
        if income_range is not None:
            try:
                taxable_array = range(*income_range)
            except:
                raise ValueError()

        cols = list(self.results(1).keys())
        results = [self.results(amount).values() for amount in taxable_array]
        df = pd.DataFrame(results, index=taxable_array, columns=cols)

        # Calculate marginal rates for each taxable amount
        marg_rate_fn = np.vectorize(lambda amount: self.marginal_rate(amount))
        marginal_rates = marg_rate_fn(taxable_array)
        df["marginal rate"] = marginal_rates

        return df

    def convert(self, rate: float):
        [rule.convert(rate) for rule in self.tax_rules]


    def df_cols(self) -> List:
        cols = list(self.sample(taxable_array=[10]).keys())
        return cols

# todo: add Sample class and implement plot