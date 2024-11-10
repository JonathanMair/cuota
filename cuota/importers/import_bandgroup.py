from cuota.data_classes.tax_rules import Band, BandsGroup
from pathlib import Path
import pandas as pd

data_path = Path(__file__).parent.parent.parent.joinpath("data")
fn = "irpf_tramos.csv"
fn2 = "cuotas2025.csv"


def get_income_tax_bands(path: Path = data_path.joinpath(fn)) -> BandsGroup:
    data = pd.read_csv(path, header=0, sep=",")
    bands = [Band(floor=floor, ceiling=ceiling, rate=rate/100)
             for floor, ceiling, rate in data.itertuples(index=False)]
    return BandsGroup(bands=bands, year=2025)


def get_social_security_bands(path: Path = data_path.joinpath(fn2)) -> BandsGroup:
    data = pd.read_csv(path, header=0, sep=",")
    for row in data.itertuples(index=False):
        a, b, c = list(row)
    bands = [Band(floor=floor, ceiling=ceiling, flat_charge=flat_charge)
             for floor, ceiling, flat_charge in data.itertuples(index=False)]
    return BandsGroup(bands=bands, year=2025)

