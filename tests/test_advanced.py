# -*- coding: utf-8 -*-

from .context import thingload

import unittest


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_thoughts(self):
        thingload.hmm()


if __name__ == '__main__':
    unittest.main()