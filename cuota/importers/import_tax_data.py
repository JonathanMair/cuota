from math import floor

from cuota.data_classes.tax_rules import Band, BandsGroup, TaxModel
from pathlib import Path
import pandas as pd
import re
from typing import List, Tuple
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


def get_from_files(regex: str) \
        -> List[Tuple]:
    """Get all files that match a pattern from the data dir and return a list of BandsGroups
    """
    data_path = Path(__file__).parent.parent.parent.joinpath("data")
    p = Path(data_path).glob('**/*')
    files_matches = [(f,  re.match(regex, str(f)).group(1)) for f in p if re.match(regex, str(f))]
    if "cuotas" in regex:
        return [(get_social_security_bands(path=f, annualized=True), year) for f, year in files_matches]
    else:
        return [(get_income_tax_bands(path=f), year) for f, year in files_matches]

def get_all_social_security_data(as_tax_model: bool=True, save_as: None | str=None) \
        -> List[TaxModel] | List[BandsGroup]:
    """Get all files that match a pattern from the data dir and return a list of TaxModels (defualt)
    or a list of BandsGroups
    """
    regex = r"^.*cuotas(20[0-9][0-9]).*\.csv$"
    years_bandsgroups = get_from_files(regex=regex)
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

def get_spanish_data_by_year() -> List[TaxModel]:
    regex_ss = r"^.*cuotas(20[0-9][0-9]).*\.csv$"
    regex_irpf = r"^.*irpf_tramos(20[0-9][0-9]).*\.csv$"
    ss_years = get_from_files(regex=regex_ss)
    irpf_years = get_from_files(regex_irpf)
    combined = [s + i for s, i in zip(ss_years, irpf_years)]
    if [year for _, year in ss_years] != [year for _, year in irpf_years]:
        raise Exception("social security and irpf years do not match, please check files")
    data = [TaxModel(tax_rules=[ss, irpf], year=year) for ss, _, irpf, year in combined]
    with open(data_path.joinpath(f"spanish_tax_rules.pickle"), "wb") as f:
        pickle.dump(data, f)
    return data

# TODO: fetch the data from the irpf_tramos files and add the appropriate bandsgroups to the taxmodels
def get_spanish_regimen_general() -> List[TaxModel]:
    years = [2022, 2023, 2024, 2025]
    rate = 6.35  / 100 # approximate % of gross charged for ss
    cap = 4500 * 12  # cap beyond which no additional charge is made
    band1 = Band(floor=0, ceiling=cap, rate=rate, exclusive=True)
    band2 = Band(floor=cap, celing=200000, flat_charge=rate * cap)
    ss_bandsgroup = BandsGroup(bands=[band1, band2], name="Régimen General")
    regex_irpf = r"^.*irpf_tramos(20[0-9][0-9]).*\.csv$"
    irpf_years = get_from_files(regex_irpf)
    irpf_dict = {int(year): bg for bg, year in irpf_years}
    return [TaxModel(tax_rules=[ss_bandsgroup, irpf_dict[year]], year=year) for year in years]