#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from bocho.utils import assemble


def main():
    """Command-line entry point for key functionality."""
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf_file')
    parser.add_argument('--pages', type=int, nargs='*')
    parser.add_argument('--width', type=int, nargs='?')
    parser.add_argument('--height', type=int, nargs='?')
    parser.add_argument('--resolution', type=int, nargs='?')
    parser.add_argument(
        '--angle', type=int, nargs='?',
        help='Angle of rotation (between -90 and 90 degrees)',
    )
    parser.add_argument('--offset_x', type=int, nargs='?')
    parser.add_argument('--offset_y', type=int, nargs='?')
    parser.add_argument('--spacing_x', type=int, nargs='?')
    parser.add_argument('--spacing_y', type=int, nargs='?')
    parser.add_argument('--zoom', type=float, nargs='?')
    parser.add_argument('--reverse', action='store_true', default=None)
    parser.add_argument('--border', type=int, nargs='?')
    parser.add_argument('--shadow', action='store_true', default=None)
    parser.add_argument('--affine', action='store_true', default=None)
    parser.add_argument('--use_convert', action='store_true', default=None)
    parser.add_argument(
        '--reuse', action='store_true', default=None,
        help='Re-use page PNG files between runs. If True, you need to clear '
             'up after yourself, but multiple runs on the same input will be '
             'much faster.',
    )
    parser.add_argument(
        '--delete', action='store_true', default=None,
        help='Delete the output file before running. If False, and the file '
             'exists, an exception will be raised and nothing will happen.',
    )
    parser.add_argument('--config', help='path to config.ini')
    parser.add_argument('--preset', help='load parameters from a named preset')
    parser.add_argument('--verbose', action='store_true', default=None)
    args = parser.parse_args()

    if not args.pdf_file[-4:] == '.pdf':
        raise Exception("Input file doesn't look like a PDF")

    kwargs = dict(args._get_kwargs())
    print assemble(args.pdf_file, **kwargs)
