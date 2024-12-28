from cuota.data_classes.tax_rules import BandsGroup, TaxModel, AllowanceFunction
from cuota.importers.import_tax_data import get_income_tax_bands

from PyCurrenciesTools import get_exchange_rate
from PyCurrenciesTools.data import CurrenciesTags


# https://www.gov.uk/government/publications/rates-and-allowances-income-tax/income-tax-rates-and-allowances-current-and-past
# https://www.gov.uk/government/publications/rates-and-allowances-national-insurance-contributions/rates-and-allowances-national-insurance-contributions

def get_conversion_rate() -> float:
    gbp_tag = CurrenciesTags.sterling
    eur_tag = CurrenciesTags.euro
    rate = 0
    try:
        rate = get_exchange_rate(gbp_tag, eur_tag)
    except Exception as e:
        print(f"Error: {e}")
    return rate

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
    path = "uk_income_tax_2025.csv"
    return get_income_tax_bands(fn=path, allowance=BritishPersonalAllowance())

def get_UK_employee_NI() -> BandsGroup:
    path = "uk_employee_NI2025.csv"
    return get_income_tax_bands(fn=path, allowance=0, name="National Insurance")

def get_UK_selfemployed_NI() -> BandsGroup:
    path = "uk_self-employed_NI2025.csv"
    return get_income_tax_bands(fn=path, allowance=0, name="National Insurance")


class UkEmployeeTaxModel(TaxModel):

    def __init__(self):
        ni = get_UK_employee_NI()
        it = get_UK_income_tax()
        super().__init__(tax_rules=[ni, it], year=2025, non_sequential=True, name="UK employee")
        self.convert(rate=get_conversion_rate())

class UkSelfEmployedTaxModel(TaxModel):

    def __init__(self):
        ni = get_UK_selfemployed_NI()
        it = get_UK_income_tax()
        super().__init__(tax_rules=[ni, it], year=2025, non_sequential=True, name="UK self-employed")
        self.convert(rate=get_conversion_rate())


if __name__ == "__main__":
    uk = UkEmployeeTaxModel()

