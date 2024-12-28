from cuota.data_classes.interfaces import AllowanceFunction
from cuota.data_classes.tax_rules import TaxModel, BandsGroup, Band
from cuota.importers.import_tax_data import get_social_security_bands, get_income_tax_bands


class SpanishAutonomoAllowance(AllowanceFunction):

    def __init__(self, allowance: int | None = None):
        self.allowance = allowance

    def function(self, taxable: int) -> int:
        min_all = SpanishMinAllowance().function(taxable=0) if self.allowance is None else self.allowance
        return min_all + 2000 if taxable * 0.7 > 2000 else min_all + int(taxable * 0.7)



class SpanishMinAllowance(AllowanceFunction):

    def function(self, taxable: int) -> int:
        return 5500


class SpanishAutonomoModel(TaxModel):

    def __init__(self, year: int, allowance: int=0):
        ss_path = f"cuotas{year}.csv"
        ss = get_social_security_bands(fn=ss_path, annualized=True)
        irpf_path = f"irpf_tramos{year}.csv"
        irpf = get_income_tax_bands(fn=irpf_path, allowance=SpanishAutonomoAllowance(allowance=allowance))
        tax_rules = [ss, irpf]
        super().__init__(tax_rules=tax_rules, year=year, name="Spanish autónomo")

class SpanishRegimenGeneralModel(TaxModel):

    def __init__(self, year: int):
        rate = 6.35 / 100  # approximate % of gross charged for ss
        cap = 4500 * 12  # cap beyond which no additional charge is made
        band1 = Band(floor=0, ceiling=cap, rate=rate, exclusive=True)
        band2 = Band(floor=cap, celing=200000, flat_charge=rate * cap)
        ss_bandsgroup = BandsGroup(bands=[band1, band2], name="Régimen General")
        irpf_path = f"irpf_tramos{year}.csv"
        irpf = get_income_tax_bands(fn=irpf_path, allowance=5500)
        tax_rules = [ss_bandsgroup, irpf]
        super().__init__(tax_rules=tax_rules, year=year, name="Spanish employee")
