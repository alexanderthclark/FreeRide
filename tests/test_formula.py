import unittest
from microecon.formula import formula

class TestFormula(unittest.TestCase):

    def setUp(self):
        s1 = 'P = 10 - 2*Q'
        s2 = 'P = 10 - 2Q'
        s3 = 'p = 2 + 4*q'
        self.affine1 = formula(s1)
        self.affine2 = formula(s2)
        self.affine3 = formula(s3)

    def test_slope(self):

        self.assertTrue(self.affine1.slope == self.affine2.slope == [-2])
        self.assertTrue(self.affine3.slope == [4])

    def tearDown(self):
        pass
