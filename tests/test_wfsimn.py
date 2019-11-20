import unittest
from test import support

# from wfsimn import generator



class MyTestCase1(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):

        wfgen = generator()
        status = wfgen.load_dfs_auto()
        print(wfgen.initialize())

    

if __name__ == '__main__':
    unittest.main()

