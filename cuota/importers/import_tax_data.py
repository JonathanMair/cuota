from math import floor

from cuota.data_classes.interfaces import AllowanceFunction
from cuota.data_classes.tax_rules import Band, BandsGroup, TaxModel
import importlib.resources as resources

import pandas as pd
import re
from typing import List, Tuple

fn = "irpf_tramos.csv"
fn2 = "cuotas2025.csv"


def get_file(fn: str):
    return resources.files("cuota.resources").joinpath(fn).open("r")

def get_income_tax_bands(
        fn: str=fn, allowance: int | AllowanceFunction = 5500, name: str= "Income Tax"
) -> BandsGroup:
    """
    Get income tax band data from a spreadsheet, at Path specified, or from a default.
    :param fn:
    :param allowance:
    :return:
    """
    data = pd.read_csv(get_file(fn), header=0, sep=",")
    bands = [Band(floor=floor, ceiling=ceiling, rate=rate/100)
             for floor, ceiling, rate in data.itertuples(index=False)]
    return BandsGroup(bands=bands, allowance=allowance, name=name)

def get_social_security_bands(fn: str=fn2, annualized: bool=True, name: str="Social Security") -> BandsGroup:
    x = 12 if annualized else 1
    data = pd.read_csv(get_file(fn), header=0, sep=",")
    for row in data.itertuples(index=False):
        a, b, c = list(row)
    bands = [Band(floor=int(floor * x), ceiling=int(ceiling * x), flat_charge=int(flat_charge * x))
             for floor, ceiling, flat_charge in data.itertuples(index=False)]
    return BandsGroup(bands=bands, name=name)


def get_from_files(regex: str) \
        -> List[Tuple]:
    """Get all files that match a pattern from the data dir and return a list of BandsGroups
    """
    p = resources.files("cuota.resources")
    files_matches = [(f,  re.match(regex, str(f)).group(1)) for f in p.iterdir() if re.match(regex, str(f))]
    if "cuotas" in regex:
        return [(get_social_security_bands(fn=f, annualized=True), year) for f, year in files_matches]
    else:
        return [(get_income_tax_bands(fn=f), year) for f, year in files_matches]

def get_all_social_security_data(as_tax_model: bool=True) \
        -> List[TaxModel] | List[BandsGroup]:
    """Get all files that match a pattern from the data dir and return a list of TaxModels (defualt)
    or a list of BandsGroups
    """
    regex = r"^.*cuotas(20[0-9][0-9]).*\.csv$"
    years_bandsgroups = get_from_files(regex=regex)
    if not as_tax_model:
        return [bandsgroup for bandsgroup, _ in years_bandsgroups]
    else:
        data = [TaxModel(year=year, tax_rules=[taxrules]) for taxrules, year in years_bandsgroups]
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


if __name__ == "__main__":
    with resources.files("cuota.resources").joinpath("cuotas2022.csv").open("r") as file:
        cuotas =  pd.read_csv(file)

    print(cuotas)
