import numpy as np
import pandas as pd
from cuota.data_classes.tax_rules import TaxModel
from cuota.logic.calculations import Calculator
from cuota.importers.import_tax_data import get_social_security_bands

from pathlib import Path
import re
from pydantic import BaseModel
from typing import List

class Comparator(): # maybe add pydantic later

    def __init__(self, models: List[TaxModel] | None):
        if len(models) > 0:
            self.models = models
            calculators = [Calculator(model) for model in models]
            dfs = [calc.calculate() for calc in calculators]
            self.dfs = dfs
            years = [model.year for model in models]
            self.years = years
            self.data = pd.concat(
                [df.assign(year=[year] * len(df.index)) for df, year in zip(dfs, years)]
            )



if __name__ == "__main__":
    data_path = Path(__file__).parent.parent.parent.joinpath("data")
    p = Path(data_path).glob('**/*')
    regex_ = r"^.*cuotas(20[0-9][0-9]).*\.csv$"
    years = [(f,  re.match(regex_, str(f)).group(1)) for f in p if re.match(regex_, str(f))]
    print(years)
    models = []
    models = [TaxModel(
                            year=match,
                            tax_rules=[get_social_security_bands(path=f, annualized=True)]
                        )
                for f, match in years
              ]
    calculators = [Calculator(model) for model in models]
    dfs = [calc.calculate() for calc in calculators]
    all_years = pd.concat(
        [df.assign(year=[year[1]] * len(df.index)) for df, year in zip(dfs, years)]
    )
    print(all_years.head())
