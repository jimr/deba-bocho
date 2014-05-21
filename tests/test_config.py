#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from bocho import config


class TestAll(unittest.TestCase):
    def setUp(self):
        self.fname = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'config.ini',
        )

    def test_load(self):
        cfg = config.load(self.fname)
        self.assertTrue(cfg.has_section('example'))

    def test_parse(self):
        cfg = config.load(self.fname)
        self.assertEqual(cfg.getint('example', 'border'), 4)
        self.assertFalse(cfg.getboolean('example', 'verbose'))

    def test_getval(self):
        cfg = config.load(self.fname)
        self.assertEqual(cfg.getval('example', 'pages'), [1,3,5,7,9])
        self.assertFalse(cfg.getval('example', 'verbose'))
        self.assertEqual(cfg.getval('example', 'border'), 4)
        self.assertEqual(cfg.getval('example', 'shear_x'), -0.3)
