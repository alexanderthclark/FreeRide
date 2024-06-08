import unittest
from freeride.formula import _formula

class TestFormula(unittest.TestCase):

    def setUp(self):
        s1 = 'P = 10 - 2*Q'
        s2 = 'P = 10 - 2Q'
        s3 = 'p = 2 + 4*q'
        self.affine1 = _formula(s1)
        self.affine2 = _formula(s2)
        self.affine3 = _formula(s3)

    def test_slope(self):

        self.assertTrue(self.affine1[1] == self.affine2[1] == -2)
        self.assertTrue(self.affine3[1] == 4)

    def tearDown(self):
        pass
