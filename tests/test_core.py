#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from PIL import Image

from bocho import assemble, DEFAULTS


class TestAll(unittest.TestCase):
    def setUp(self):
        self.fname = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '1405.0032.pdf',
        )

    def cleanup(self, fname):
        os.remove(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                fname,
            )
        )

    def test_basic_stack(self):
        output = assemble(self.fname)
        img = Image.open(output)

        self.assertEqual(
            img.size, (DEFAULTS.get('width'), DEFAULTS.get('height'))
        )

        self.cleanup(output)
