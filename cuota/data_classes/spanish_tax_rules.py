from cuota.data_classes.interfaces import AllowanceFunction


class SpanishAutonomoAllowance(AllowanceFunction):

    def function(self, taxable: int) -> int:
        return 2000 if taxable * 0.7 < 2000 else taxable * 0.7
