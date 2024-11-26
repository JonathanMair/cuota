import logging
from cuota.data_classes.tax_rules import Band, BandsGroup, TaxModel
from cuota.importers.import_tax_data import get_social_security_bands, get_income_tax_bands

logger = logging.getLogger()


def test_Band():
    b = Band(floor=0, ceiling=10000, rate=0.1)
    p = b.get_payable(5000)
    assert p == 500


def test_BandsGroup():
    # sample case:
    # 0-10k 0%, 10-20k: 10%, 20-30k: 20%
    # income = 35k - 10k allowance = 25k => 0 + 1000 + 1000
    # payable = 2000
    floors = [0, 10000, 20000]
    ceilings = [10000, 20000, 30000]
    rates = [0, 0.1, 0.2]
    allowance = 10000
    income = 35000
    bands = [Band(floor=floor, ceiling=ceiling, rate=rate) for
             floor, ceiling, rate in zip(floors, ceilings, rates)]
    bandsgroup = BandsGroup(bands=bands, allowance=allowance)
    assert bandsgroup.get_payable(income) == 2000


def test_BandsGroup_flat_charge():
    # sample case:
    # 0-10k 250, 10-20k: 400, 20-30k: 500
    # income = 25k => 250 + 400 + 1150
    # payable = 2000
    floors = [0, 10000, 20000]
    ceilings = [10000, 20000, 30000]
    flat_charges = [250, 400, 500]
    income = 28000
    bands = [Band(floor=floor, ceiling=ceiling, flat_charge=flat_charge) for
             floor, ceiling, flat_charge in zip(floors, ceilings, flat_charges)]
    bandsgroup = BandsGroup(bands=bands)
    assert bandsgroup.get_payable(income) == 500


def test_import_bandgroup_social_security():
    ss_bands = get_social_security_bands()
    print(ss_bands.get_payable(33000))
    assert True



