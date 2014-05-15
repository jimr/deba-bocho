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
    """Type-aware configuration parser.

    We avoid the need for messy ``getfloat`` etc lookups elsewhere in the code
    by recording which parameters are of which type, and offering a new
    ``getval`` method that automatically does the Right Thing.

    """
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
                result = list(map(int, result.split(',')))
        return result


def load(fname=None):
    """Load and return configuration from a file.

    Args:
        fname (str): Path to the ini file we should use. If not provided, we
            default to $HOME/.config/bocho/config.ini

    Returns:
        The parsed configuration

    Raises:
        ConfigurationError: if the file can't be found.

    """
    if not fname:
        fname = os.path.join(
            os.getenv('HOME'), '.config', 'bocho', 'config.ini'
        )

    if not os.path.exists(fname):
        raise ConfigurationError(
            "Unable to find configuration file."
        )

    config = CustomConfigParser()
    config.read(fname)

    return config
