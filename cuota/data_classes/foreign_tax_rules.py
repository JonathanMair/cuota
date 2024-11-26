from cuota.data_classes.tax_rules import Band, BandsGroup, TaxModel, AllowanceFunction
from cuota.importers.import_tax_data import get_social_security_bands, get_income_tax_bands, DATA_PATH

from pathlib import Path
import pandas as pd


# https://www.gov.uk/government/publications/rates-and-allowances-income-tax/income-tax-rates-and-allowances-current-and-past
# https://www.gov.uk/government/publications/rates-and-allowances-national-insurance-contributions/rates-and-allowances-national-insurance-contributions


class BritishPersonalAllowance(AllowanceFunction):

    def function(self, taxable: int) -> int:
        if taxable < 100000:
            allowance = 12570
        else:
            difference = taxable - 100000
            if difference < 12570:
                allowance = 12570 - difference
            else:
                allowance = 0
        return allowance


def get_UK_income_tax() -> BandsGroup:
    path = DATA_PATH.joinpath("uk_income_tax_2025.csv")
    return get_income_tax_bands(path=path, allowance=BritishPersonalAllowance())

def get_UK_employee_NI() -> BandsGroup:
    path = DATA_PATH.joinpath("uk_employee_NI2025.csv")
    return get_income_tax_bands(path=path, allowance=0)


class UkEmployeeTaxModel(TaxModel):

    def __init__(self):
        ni = get_UK_employee_NI()
        it = get_UK_income_tax()
        super().__init__(tax_rules=[ni, it], year=2025, non_sequential=True, name="UK employee")



if __name__ == "__main__":
    uk = UkEmployeeTaxModel()
    uk.results(40000)