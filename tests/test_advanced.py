# -*- coding: utf-8 -*-

from .context import fanthing

import unittest


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_thoughts(self):
        fanthing.hmm()


if __name__ == '__main__':
    unittest.main()