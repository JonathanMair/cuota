from cuota.data_classes.tax_rules import TaxModel
from cuota.importers.import_tax_data import get_income_tax_bands, get_social_security_bands
import pandas as pd
import numpy as np


class Calculator:

    def __init__(self, sample: bool = True):
        self.tax_model = self.sample()

    def sample(self):
        return TaxModel(tax_rules=[get_social_security_bands(), get_income_tax_bands()])

    def get_income_sample(self, min: int = 3600, max: int = 120000, interval: int = 100) -> np.array:
        return np.array(range(min, max, interval))

    def get_payable_by_income(self, income_sample: np.array) -> pd.DataFrame:
        fn = np.vectorize(lambda income: self.tax_model.get_payable(income))
        net_income = fn(income_sample)
        return pd.DataFrame({"gross income": income_sample, "net income": net_income})


c = Calculator()
s = c.get_income_sample()
print(c.get_payable_by_income(s).head())