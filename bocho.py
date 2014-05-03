#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import shlex
import os
import subprocess
import tempfile

from pyPdf import PdfFileReader
from PIL import Image, ImageDraw

DEFAULTS = {
    'pages': range(1, 6),
    'width': 630,  # pixels
    'height': 290,  # pixels
    'angle': 0,  # degrees anti-clockwise from vertical
    'offset': 0,  # pixels
    'spacing': 107,  # pixels
}

ASPECT = 0.7  # approximate A4 aspect ratio


def _slice_page(fname, index, verbose=False):
    "Call out to ImageMagick to convert a page into a PNG"
    fd, out_path = tempfile.mkstemp('.png', 'bocho-')
    os.close(fd)

    command = "convert -density 400 -scale 1200x1700 '%s[%d]' %s"
    command = command % (fname, index, out_path)
    sh_args = shlex.split(str(command))

    if verbose:
        print 'processing page %d: %s' % (index, command)

    ret = subprocess.call(sh_args)

    # Non-zero return code means failure.
    if ret != 0:
        raise Exception(
            'Unable to generate PNG from page %d:\n  %s' %
            (index, command)
        )

    return out_path


def bocho(fname, pages=None, width=None, height=None, angle=None, offset=None,
          spacing=None, verbose=False):
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

    page_width = height * ASPECT
    page_images = [
        Image.open(_slice_page(fname, x - 1, verbose)).convert('RGB')
        for x in pages
    ]
    x_coords = [
        offset + x * spacing for x in range(len(pages))
    ]

    outfile = Image.new('RGB', (width, height))
    for x, img in enumerate(reversed(page_images), 1):
        # Draw lines down the right edges of each page to provide visual
        # separation. Cheap drop-shadow basically.
        draw = ImageDraw.Draw(img)
        xy = ((img.size[0] - 2, 0), (img.size[0] - 2, img.size[1]))
        print 'drawing a line between %s and %s' % xy
        draw.line(xy, fill='black', width=2)

        # This really doesn't work well at all.
        if angle != 0:
            img = img.rotate(angle, Image.BILINEAR)

        img = img.resize((int(page_width), height), Image.ANTIALIAS)

        coords = (x_coords[-x], 0)
        if verbose:
            print 'placing page %d at %s' % (pages[-x], coords)
        outfile.paste(img, coords)

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
    parser.add_argument(
        '--verbose', action='store_true', default=False,
    )
    parser.add_argument('--pages', type=int, nargs='*')
    parser.add_argument('pdf_file')
    args = parser.parse_args()

    if not args.pdf_file[-4:] == '.pdf':
        raise Exception("Input file doesn't look like a PDF")

    print bocho(
        args.pdf_file, args.pages, args.width, args.height, args.angle,
        args.offset, args.spacing, args.verbose,
    )
