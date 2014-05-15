#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from ConfigParser import SafeConfigParser as ConfigParser
except ImportError:  # py3k
    import sys
    minor = sys.version_info[1]
    if minor >= 2:
        # SafeConfigParser is deprecated as of 3.2
        from configparser import ConfigParser
    else:
        from configparser import SafeConfigParser as ConfigParser


class ConfigurationError(Exception):
    pass


class CustomConfigParser(ConfigParser):
    def getval(self, section, name):
        int_lists = ['pages']
        floats = ['angle', 'zoom']
        ints = [
            'width', 'height', 'border', 'spacing_x', 'spacing_y', 'offset_x',
            'offset_y',
        ]
        bools = [
            'shadow', 'affine', 'reverse', 'reuse', 'delete', 'use_convert',
        ]
        if name in floats:
            result = self.getfloat(section, name)
        elif name in ints:
            result = self.getint(section, name)
        elif name in bools:
            result = self.getboolean(section, name)
        else:
            result = self.get(section, name)
            if name in int_lists:
                result = map(int, result.split(','))
        return result


def load(fname=None):
    if not fname:
        fnames = []
        # If we're running from a .pyc file, there won't be a symlink, so
        # finding our way back to the config.ini won't work unless we do it
        # from the symlinked .py file.
        this_file = __file__
        if this_file.endswith('.pyc'):
            this_file = this_file[:-1]

        fname = os.path.join(
            os.path.dirname(os.path.realpath(this_file)),
            'config.ini',
        )
        fnames.append(fname)

        # Check for $HOME/.config/pathfix/config.ini
        if not os.path.exists(fname):
            fname = os.path.join(
                os.getenv('HOME'), '.config', 'bocho', 'config.ini'
            )
            fnames.append(fname)

        if not os.path.exists(fname):
            raise ConfigurationError(
                "Unable to find configuration file. Tried:\n * %s" %
                '\n * '.join(fnames)
            )

    config = CustomConfigParser()
    config.read(fname)

    return config
