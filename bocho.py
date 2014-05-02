#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os

DEFAULTS = {
    'pages': range(1, 6),
    'width': 630,  # pixels
    'height': 290,  # pixels
    'angle': 30,  # degrees clockwise from vertical
    'offset': 230,  # pixels
    'spacing': 125,  # pixels
}


def bocho(fname, pages=None, width=None, height=None, angle=None, offset=None,
          spacing=None):
    pages = pages or DEFAULTS.get('pages')
    width = width or DEFAULTS.get('width')
    height = height or DEFAULTS.get('height')
    angle = angle or DEFAULTS.get('angle')
    offset = offset or DEFAULTS.get('offset')
    spacing = spacing or DEFAULTS.get('spacing')

    file_path = '%s-bocho-%sx%s.png' % (fname[:-4], width, height)
    if os.path.exists(file_path):
        raise Exception("%s already exists, not overwriting" % file_path)

    return file_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--width', type=int, nargs='?', default=DEFAULTS.get('width'),
    )
    parser.add_argument(
        '--height', type=int, nargs='?', default=DEFAULTS.get('height'),
    )
    parser.add_argument(
        '--angle', type=int, nargs='?', default=DEFAULTS.get('angle'),
    )
    parser.add_argument(
        '--offset', type=int, nargs='?', default=DEFAULTS.get('offset'),
    )
    parser.add_argument(
        '--spacing', type=int, nargs='?', default=DEFAULTS.get('spacing'),
    )
    parser.add_argument('--pages', type=int, nargs='*')
    parser.add_argument('pdf_file')
    args = parser.parse_args()

    if not args.pdf_file[-4:] == '.pdf':
        raise Exception("Input file doesn't look like a PDF")

    print bocho(
        args.pdf_file, args.pages, args.width, args.height, args.angle,
        args.offset, args.spacing,
    )
