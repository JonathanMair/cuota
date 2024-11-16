from cuota.data_classes.tax_rules import TaxModel
from cuota.importers.import_tax_data import get_income_tax_bands, get_social_security_bands
import pandas as pd
import numpy as np
from collections import OrderedDict


class Calculator:

    metrics = {
        "PAYABLE": "payable",
        "PAYABLE_SEQ": "payable in sequence",
        "NET_THIS": "net of this metric",
        "NET_SEQ": "net in sequence",
        "EFFECTIVE_THIS": "effective rate",
        "EFFECTIVE_SEQ": "effective in sequence"
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

        # for each rule: payable after application of this rule
        for i, rule in enumerate(rules, 1):
            rule_fn = np.vectorize(lambda gross: rule.get_payable(gross))
            results.append(rule_fn(gross_array))

        # for each rule: payable applying rules in sequence
        results.append(results[0])  # because the first in the sequence will be the same as first item in prev operation
        [results.append(results[i - 1] + results[i]) for i in range(1, len(rules))]

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
        results.extend([results[i] / gross_array for i in range(len(rules))])

        # for each rule: effective rate after applying rule in sequence
        running_total = np.zeros(len(gross_array))
        [results.append(
            (results[i + len(rules)] + running_total) / gross_array)
            for i, _ in enumerate(rules)
        ]


        # columns and index provided backwards then transposed because df constructor expects data arrays to be rows
        df = pd.DataFrame(results, columns=gross_array, index=columns).T
        return df




if __name__ == "__main__":
    c = Calculator()
    print(c.data.head())
    print(c.data.columns)






