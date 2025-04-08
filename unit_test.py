import unittest
import numpy as np
from Lazors import reader, solver

class TestPosCheck(unittest.TestCase):
    ''' testing of pos_check function'''
    def test_1(self): 
        grid=np.zeros((3,3),dtype=str)
        self.assertFalse(solver.pos_check((-1,1),grid)) 
        # testing lower limit in x

    def test_2(self):
        grid=np.zeros((3,3),dtype=str)
        self.assertFalse(solver.pos_check((1,-1),grid))
        # testing lower limit in y

    def test_3(self):
        grid=np.zeros((2,3),dtype=str)
        self.assertFalse(solver.pos_check((0,2),grid))
        # testing upper limit in y
    
    def test_4(self):
        grid=np.zeros((2,3),dtype=str)
        self.assertFalse(solver.pos_check((5,1),grid))
        # testing upper limit in x


if __name__=='__main__':
    unittest.main()