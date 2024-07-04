import unittest
from freeride.formula import _formula

class TestFormula(unittest.TestCase):

    def setUp(self):
        s1 = 'P = 10 - 2*Q'
        s2 = 'P = 10 - 2Q'
        s3 = 'p = 2 + 4*q'
        s4 = 'y = 1*x'
        s5 = 'x = 2y'
        s6 = 'y=x'

        self.affine1 = _formula(s1)
        self.affine2 = _formula(s2)
        self.affine3 = _formula(s3)
        self.affine4 = _formula(s4)
        self.affine5 = _formula(s5)
        self.affine6 = _formula(s6)

    def test_coef(self):

        self.assertTrue(self.affine1[1] == self.affine2[1] == -2)
        self.assertTrue(self.affine3[1] == 4)
        self.assertTrue(self.affine4[0] == 0)
        self.assertTrue(self.affine4[1] == 1)
        self.assertTrue(self.affine5[0] == 0)
        self.assertTrue(self.affine5[1] == 0.5)
        self.assertTrue(self.affine6[0] == 0)
        self.assertTrue(self.affine6[1] == 1)

    def tearDown(self):
        pass
