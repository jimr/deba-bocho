#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shlex
import subprocess
import unittest


class TestAll(unittest.TestCase):
    def test_os_deps(self):
        sh_args = shlex.split("convert -h")
        retcode = subprocess.Popen(sh_args, stdout=subprocess.PIPE).wait()
        self.assertEqual(retcode, 0)
