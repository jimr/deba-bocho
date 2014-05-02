#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import shlex
import os
import subprocess
import tempfile

from pyPdf import PdfFileReader
from PIL import Image

DEFAULTS = {
    'pages': range(1, 6),
    'width': 630,  # pixels
    'height': 290,  # pixels
    'angle': 0,  # degrees anti-clockwise from vertical
    'offset': 230,  # pixels
    'spacing': 125,  # pixels
}

ASPECT = 0.7  # approximate A4 aspect ratio


def _slice_page(fname, index):
    fd, out_path = tempfile.mkstemp('.png', 'bocho-')
    os.close(fd)

    command = "convert -density 400 -scale 1200x1700 %s[%d] %s"
    command = command % (fname, index, out_path)
    sh_args = shlex.split(str(command))

    # Non-zero return code implies failure.
    ret = subprocess.call(sh_args)
    if ret != 0:
        raise Exception('Unable to generate PNG from page %d' % index)

    print out_path
    return out_path


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

    infile = PdfFileReader(file(fname, "rb"))

    if any([x > infile.numPages for x in pages]):
        raise Exception(
            'Some pages are outside of the input document. '
            '(it is %d pages long)' % infile.numPages
        )

    page_images = [
        Image.open(_slice_page(fname, x - 1)) for x in pages
    ]

    outfile = Image.new('RGB', (width, height))
    for x, img in enumerate(reversed(page_images), 1):
        img = img.convert('RGB')
        img = img.resize((int(height * ASPECT), height), Image.ANTIALIAS)
        if angle != 0:
            img = img.rotate(angle)

        outfile.paste(img, (width - (spacing * x), 0))

    outfile.save(file_path)

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
