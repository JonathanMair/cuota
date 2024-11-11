from cuota.data_classes.tax_rules import TaxModel
from cuota.importers.import_tax_data import get_income_tax_bands, get_social_security_bands
import pandas as pd
import numpy as np
from collections import OrderedDict


class Calculator:

    def __init__(self, tax_model: TaxModel | None=None):
        self.tax_model = self.sample() if tax_model is None else tax_model
        self.income_sample = self.get_income_sample()
        self.data = self.calculate()

    def sample(self):
        return TaxModel(tax_rules=[get_social_security_bands(), get_income_tax_bands()])

    def get_income_sample(self, min: int = 3600, max: int = 120000, interval: int = 100) -> np.array:
        return np.array(range(min, max, interval))

    def calculate(self) -> pd.DataFrame:
        rules = self.tax_model.tax_rules
        gross_array = self.income_sample

        # for each rule: payable, net after application of this rule
        working_array = gross_array.copy()
        results = OrderedDict()
        results["gross income"] = gross_array
        payable_cols = OrderedDict()
        for i, rule in enumerate(rules, 1):
            rule_fn = np.vectorize(lambda gross: rule.get_payable(gross))
            payable_array = rule_fn(working_array)
            col = f"Payable ({i} {rule.name})"
            payable_cols[i] = col
            results[col] = payable_array.copy()
            working_array = gross_array.copy()

        # for each rule: net after sequential application
        working_array = gross_array.copy()
        for i, rule in enumerate(rules, 1):
            net = np.subtract(working_array, results[payable_cols[i]])
            col = f"Net ({i} {rule.name})"
            results[col] = net.copy()
            working_array = net.copy()

        df = pd.DataFrame(results)
        return df



if __name__ == "__main__":
    c = Calculator()
    print(c.data.head())
    print(c.data.columns)






