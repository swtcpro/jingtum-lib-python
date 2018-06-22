import sys 
sys.path.append("..\src")
import utils
import unittest

class UtilTestCase(unittest.TestCase):
    def testToArray(self):
        self.assertEqual(utils.toArray('1234', 'hex'),[ 0x12, 0x34 ],'err')
        self.assertEqual(utils.toArray('1234'),[ 49, 50, 51, 52 ],'err')
        self.assertEqual(utils.toArray('1234', 'utf8'),[ 49, 50, 51, 52 ],'err')
        self.assertEqual(utils.toArray('\u1234234'),[ 18, 52, 50, 51, 52 ],'err')
        self.assertEqual(utils.toArray([ 1, 2, 3, 4 ]),[ 1, 2, 3, 4 ],'err')

    def testZero2(self):
        # it('should zero pad byte to hex', () ,> {
        self.assertEqual(utils.zero2('0'),'00','testZero2 0 err')
        self.assertEqual(utils.zero2('01'),'01','testZero2 01 err')

    def testToHex(self):
        # it('should convert to hex', () ,> {
        self.assertEqual(utils.toHex([ 0, 1, 2, 3 ]),'00010203','toHex err')

    def testEncode(self):
        self.assertEqual(utils.encode([ 0, 1, 2, 3 ]), [ 0, 1, 2, 3 ])
        self.assertEqual(utils.encode([ 0, 1, 2, 3 ], 'hex'), '00010203')
unittest.main()

