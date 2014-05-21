#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from bocho import utils


class TestAll(unittest.TestCase):
    def test_px(self):
        self.assertEqual(utils.px(0.1), 0)
        self.assertEqual(utils.px(0.6), 1)
