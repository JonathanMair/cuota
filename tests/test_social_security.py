from cuota.data_classes.social_security import Band

def test_Band():
    b = Band(floor=0, ceiling=10000, rate=0.1)
    p = b.get_payable(5000)
    assert p == 500
