import sys 
sys.path.append("..\src")
import ec
import unittest
ec = ec.EC('secp256k1')

"""
class ecTestCase(unittest.TestCase):
    def testEcInit(self):
        self.assertEqual(utils.toArray('1234', 'hex'),[ 0x12, 0x34 ],'toArray err')
        self.assertEqual(utils.toArray('1234'),[ 49, 50, 51, 52 ],'toArray err')
        self.assertEqual(utils.toArray('1234', 'utf8'),[ 49, 50, 51, 52 ],'toArray err')
        self.assertEqual(utils.toArray('\u1234234'),[ 18, 52, 50, 51, 52 ],'toArray err')
        self.assertEqual(utils.toArray([ 1, 2, 3, 4 ]),[ 1, 2, 3, 4 ],'toArray err')
"""

#unittest.main()

