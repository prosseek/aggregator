__author__ = 'smcho'

import unittest
import sys

sys.path.append("../src")

from treeGen import *


class TestTreeGen(unittest.TestCase):
    def setUp(self):
        self.tree_gen = TreeGen()

    def test_get_depth(self):
        tree = [(0, None),
                (1, 0), (2, 0), (3, 0),
                (4, 1), (5, 1), (6, 2), (7, 2),
                (8, 4), (9, 4), (10, 4), (11, 5), (12, 6), (13, 6), (14, 7), (15, 7),
                (16, 8), (17, 8), (18, 8), (19, 8)]
        result = TreeGen.get_depth(tree)
        self.assertEqual(result, 4)

    def test_generate_exception(self):
        # (2^3 - 1)(2 - 1) = 7 is the maximum node to create, so it should raise an error.
        self.assertRaises(Exception, self.tree_gen.generate, (20, 2, 3))

    def test_generate(self):
        tree, depth = self.tree_gen.generate(10, 4, 4)
        self.assertTrue(len(tree) == 10)
        # Generated depth should be less than given depth
        self.assertTrue(depth <= 4, "Depth is %d" % depth)

    def test_format_converter(self):
        tree = [(0, None),
                (1, 0), (2, 0), (3, 0),
                (4, 1), (5, 1), (6, 2), (7, 2),
                (8, 4), (9, 4), (10, 4), (11, 5), (12, 6), (13, 6), (14, 7), (15, 7),
                (16, 8), (17, 8), (18, 8), (19, 8)]
        result = TreeGen.format_converter(tree)
        expected = {0: [1, 2, 3], 1: [4, 5], 2: [6, 7], 4: [8, 9, 10], 5: [11], 6: [12, 13], 7: [14, 15], 8: [16, 17, 18, 19]}
        self.assertTrue(result == expected)

    def test_tree_gen(self):
        for i in range(10):
            a,b = TreeGen.get_two_node_values(100)
            self.assertTrue(a < b, "Error b (%d) is not bigger than a (%d)" % (b, a))

if __name__ == "__main__":
    unittest.main(verbosity=2)