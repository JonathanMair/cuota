from cuota.data_classes.tax_rules import TaxModel
from cuota.logic.calculations import Calculator
from cuota.importers.import_tax_data import get_social_security_bands

from pathlib import Path
import re





if __name__ == "__main__":
    data_path = Path(__file__).parent.parent.parent.joinpath("data")
    p = Path(data_path).glob('**/*')
    regex_ = r"^.*cuotas(20[0-9][0-9]).*\.csv$"
    years = [(f,  re.match(regex_, str(f))) for f in p if re.match(regex_, str(f))]
    models = []
    models = [TaxModel(
                            year=match.group(1),
                            tax_rules=[get_social_security_bands(path=f, annualized=True)]
                        )
                for f, match in years
              ]
    print(models)