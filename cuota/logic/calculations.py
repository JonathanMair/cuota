from cuota.data_classes.tax_rules import TaxModel
from cuota.importers.import_tax_data import get_income_tax_bands, get_social_security_bands
import pandas as pd
import numpy as np
from collections import OrderedDict


class Calculator:

    metrics = {
        "PAYABLE": "payable",
        "_NET_THIS": "net of this metric",
        "_NET_SEQ": "net in sequence",
        "_EFFECTIVE_THIS": "effective rate",
        "_EFFECTIVE_SEQ": "effective in sequence"
    }

    def __init__(self, tax_model: TaxModel | None=None):
        self.tax_model = self.sample() if tax_model is None else tax_model
        self.income_sample = self.get_income_sample()
        self.data = self.calculate()

    def sample(self):
        return TaxModel(tax_rules=[get_social_security_bands(), get_income_tax_bands()])

    def get_income_sample(self, min: int = 6000, max: int = 72000, interval: int = 100) -> np.array:
        return np.array(range(min, max, interval))

    def calculate(self) -> pd.DataFrame:
        rules = self.tax_model.tax_rules
        gross_array = self.income_sample

        # construct multiindex: (a) rules, (b) payable, net of this, net in sequence,
        # effective rate, effective in sequence
        tuples = [(rule.name, metric) for metric in self.metrics.values() for rule in rules]
        columns = pd.MultiIndex.from_tuples(tuples=tuples)
        results = []

        # for each rule: payable, net after application of this rule
        for i, rule in enumerate(rules, 1):
            rule_fn = np.vectorize(lambda gross: rule.get_payable(gross))
            results.append(rule_fn(gross_array))

        # for each rule: income net of this rule only
        for i, rule in enumerate(rules, 1):
            rule_fn = np.vectorize(lambda gross: gross - rule.get_payable(gross))
            results.append(rule_fn(gross_array))

        # for each rule: net after sequential application
        working_array = gross_array.copy()
        for i, rule in enumerate(rules):
            net = np.subtract(working_array, results[i])
            results.append(net)
            working_array = net.copy()

        # for each rule: effective rate after applying this rule only
        for i, rule in enumerate(rules):
            results.append(np.divide(results[i], gross_array))

        # for each rule: effective rate after applying rule in sequence
        for i, rule in enumerate(rules):
            results.append(np.divide(results[i + 5], gross_array))

        # columns and index provided backwards then transposed because df constructor expects data arrays to be rows
        df = pd.DataFrame(results, columns=gross_array, index=columns).T
        return df



if __name__ == "__main__":
    c = Calculator()
    print(c.data.head())
    print(c.data.columns)






