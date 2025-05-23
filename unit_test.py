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

class TestGetOpens(unittest.TestCase):
    def test_1(self):
        grid=np.array([['o','o']])
        self.assertTrue(len(solver.get_open(grid))==2)
        # testing that it finds the right number of opens

    def test_2(self):
        grid=np.zeros((3,3),dtype=str)
        grid[1,2]='o'
        space=solver.get_open(grid)[0]
        self.assertTrue(space[0]==2 and space[1]==1)
        # testing that it gets the xy values correct

class TestGetConfigs(unittest.TestCase):
    def test_1(self):
        grid=np.array([['o','o']])
        configs=solver.get_configs(grid,(1,1,0))
        self.assertTrue(len(configs)==2)
        # should be 2 configs (A,B or B,A)

    def test_2(self):
        grid=np.array([['o','o'],['B','o']])
        configs=solver.get_configs(grid,(0,0,1))
        self.assertTrue(len(configs)==3)
        # should be 3 configs (C placed in any of the three opens)

if __name__=='__main__':
    unittest.main()