#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import math
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
    'offset_x': 0,  # pixels
    'offset_y': 0,  # pixels
    'spacing': 107,  # pixels
    'zoom': 1.0,
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


def bocho(fname, pages=None, width=None, height=None, angle=None,
          offset_x=None, offset_y=None, spacing=None, zoom=None,
          verbose=False):
    pages = pages or DEFAULTS.get('pages')
    width = width or DEFAULTS.get('width')
    height = height or DEFAULTS.get('height')
    angle = angle or DEFAULTS.get('angle')
    offset_x = offset_x or DEFAULTS.get('offset_x')
    offset_y = offset_y or DEFAULTS.get('offset_y')
    spacing = spacing or DEFAULTS.get('spacing')
    zoom = zoom or DEFAULTS.get('zoom')

    assert -90 <= angle <= 90

    angle = math.radians(angle)

    file_path = '%s-bocho-%sx%s.png' % (fname[:-4], width, height)
    if os.path.exists(file_path):
        raise Exception("%s already exists, not overwriting" % file_path)

    infile = PdfFileReader(file(fname, "rb"))

    if any([x > infile.numPages for x in pages]):
        raise Exception(
            'Some pages are outside of the input document. '
            '(it is %d pages long)' % infile.numPages
        )

    n = len(pages)
    page_height = int(height * zoom)
    page_width = page_height * ASPECT
    x_spacing = spacing
    y_spacing = 0

    if angle:
        y_spacing = spacing * math.cos(angle)
        x_spacing = abs(y_spacing / math.tan(angle))

    if verbose:
        print 'spacing: %s' % str((x_spacing, y_spacing))

    page_images = [
        Image.open(_slice_page(fname, x - 1, verbose)).convert('RGB')
        for x in pages
    ]

    # If there's no angle specified then all the y coords will be zero and the
    # x coords will be a multiple of the provided spacing plus the offset.
    x_coords = map(int, [i * x_spacing for i in range(n)])
    y_coords = map(int, [i * y_spacing for i in range(n)])

    if angle < 0:
        y_coords.sort(reverse=True)

    size = (width, height)
    if angle != 0:
        # If we're rotating the pages, we stack them up with appropriate
        # horizontal and vertical offsets first, then we rotate the result.
        # Because of this, we must expand the output image to be large enough
        # to fit the unrotated stack. The rotation operation below will expand
        # the output image enough so everything still fits, but this bit we
        # need to figure out for ourselves in advance.
        size = (
            int((page_width * n) - (page_width - x_spacing) * (n - 1)),
            int(page_height + max(y_coords))
        )

    outfile = Image.new('RGB', size)

    if verbose:
        print 'output size before rotating: %s' % str(size)

    for x, img in enumerate(reversed(page_images), 1):
        # Draw lines down the right and bottom edges of each page to provide
        # visual separation. Cheap drop-shadow basically.
        # Right-hand edges first...
        draw = ImageDraw.Draw(img)
        xy = ((img.size[0] - 2, 0), (img.size[0] - 2, img.size[1]))
        if verbose:
            print 'drawing a line between %s and %s' % xy
        draw.line(xy, fill='black', width=2)

        # ...then bottom edges.
        xy = ((0, img.size[1] - 2), (img.size[0], img.size[1] - 2))
        if verbose:
            print 'drawing a line between %s and %s' % xy
        draw.line(xy, fill='black', width=2)

        img = img.resize((int(page_width), page_height), Image.ANTIALIAS)

        coords = (x_coords[-x], y_coords[-x])
        if verbose:
            print 'placing page %d at %s' % (pages[-x], coords)
        outfile.paste(img, coords)

    if angle != 0:
        outfile = outfile.rotate(math.degrees(angle), Image.BILINEAR, True)
        if verbose:
            print 'output size before cropping: %s' % str(outfile.size)

        # Rotation is about the center (and expands to fit the result), so
        # cropping is simply a case of positioning a rectangle of the desired
        # width & height about the center of the rotated image.
        left = int((outfile.size[0] - width) / 2) - offset_x
        top = int((outfile.size[1] - height) / 2) - offset_y
        outfile = outfile.crop((left, top, left + width, top + height))

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
        help='Angle of rotation (between -90 and 90 degrees)',
    )
    parser.add_argument(
        '--offset_x', type=int, nargs='?', default=DEFAULTS.get('offset_x'),
    )
    parser.add_argument(
        '--offset_y', type=int, nargs='?', default=DEFAULTS.get('offset_y'),
    )
    parser.add_argument(
        '--spacing', type=int, nargs='?', default=DEFAULTS.get('spacing'),
    )
    parser.add_argument(
        '--zoom', type=float, nargs='?', default=DEFAULTS.get('zoom'),
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
        args.offset_x, args.offset_y, args.spacing, args.zoom, args.verbose,
    )
