from cuota.data_classes.tax_rules import Band, BandsGroup, TaxModel
from pathlib import Path
import pandas as pd
import re
from typing import List
from pathlib import Path
import pickle

data_path = Path(__file__).parent.parent.parent.joinpath("data")
fn = "irpf_tramos.csv"
fn2 = "cuotas2025.csv"


def get_income_tax_bands(path: Path = data_path.joinpath(fn), allowance: int = 5500) -> BandsGroup:
    """
    Get income tax band data from a spreadsheet, at Path specified, or from a default.
    :param path:
    :param allowance:
    :return:
    """
    data = pd.read_csv(path, header=0, sep=",")
    bands = [Band(floor=floor, ceiling=ceiling, rate=rate/100)
             for floor, ceiling, rate in data.itertuples(index=False)]
    return BandsGroup(bands=bands, year=2025, allowance=allowance, name="Income Tax")


def get_social_security_bands(path: Path = data_path.joinpath(fn2), annualized: bool=True) -> BandsGroup:
    x = 12 if annualized else 1
    data = pd.read_csv(path, header=0, sep=",")
    for row in data.itertuples(index=False):
        a, b, c = list(row)
    bands = [Band(floor=int(floor * x), ceiling=int(ceiling * x), flat_charge=int(flat_charge * x))
             for floor, ceiling, flat_charge in data.itertuples(index=False)]
    return BandsGroup(bands=bands, name="Social Security")


def get_all_social_security_data(as_tax_model: bool=True, save_as: None | str=None) \
        -> List[TaxModel] | List[BandsGroup]:
    """Get all files that match a pattern from the data dir and return a list of TaxModels (defualt)
    or a list of BandsGroups
    """
    data_path = Path(__file__).parent.parent.parent.joinpath("data")
    p = Path(data_path).glob('**/*')
    regex_ = r"^.*cuotas(20[0-9][0-9]).*\.csv$"
    files_matches = [(f,  re.match(regex_, str(f)).group(1)) for f in p if re.match(regex_, str(f))]
    years_bandsgroups = [(get_social_security_bands(path=f, annualized=True), year) for f, year in files_matches]
    if not as_tax_model:
        data = [bandsgroup for bandsgroup, _ in years_bandsgroups]
        if save_as is not None:
            with open(data_path.joinpath(f"social_security_bandsgroups_{save_as}.pickle"), "wb") as f:
                pickle.dump(data, f)
        return data
    else:
        data = [TaxModel(year=year, tax_rules=[taxrules]) for taxrules, year in years_bandsgroups]
        if save_as is not None:
            with open(data_path.joinpath(f"social_security_tax_rules_{save_as}.pickle"), "wb") as f:
                pickle.dump(data, f)
        return data
