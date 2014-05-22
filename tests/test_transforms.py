#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from PIL import Image

from bocho import transforms


class TestAll(unittest.TestCase):
    def setUp(self):
        self.fname = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'house.tiff',
        )

    def test_shear_resize(self):
        img = Image.open(self.fname)
        self.assertEqual(img.size, (512, 512))

        shear_x = transforms.shear(img, x=0.5)
        self.assertEqual(shear_x.size, (512 + 256, 512))

        shear_y = transforms.shear(img, y=0.5)
        self.assertEqual(shear_y.size, (512, 512 + 256))

        shear_both = transforms.shear(img, 0.5, 0.5)
        self.assertEqual(shear_both.size, (512 + 256, 512 + 256))
