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

def log(msg):
    if VERBOSE:
        print msg


def px(number):
    # Round a float & make it a valid pixel value. Bit more accurate than just int.
    return int(round(number))


def _slice_page(fname, index):
    "Call out to ImageMagick to convert a page into a PNG"
    fd, out_path = tempfile.mkstemp('.png', 'bocho-')
    os.close(fd)

    command = "convert -density 400 -scale 1200x1700 '%s[%d]' %s"
    command = command % (fname, index, out_path)
    sh_args = shlex.split(str(command))

    log('processing page %d: %s' % (index, command))

    ret = subprocess.call(sh_args)

    # Non-zero return code means failure.
    if ret != 0:
        raise Exception(
            'Unable to generate PNG from page %d:\n  %s' %
            (index, command)
        )

    return out_path


def _add_border(img, fill='black', width=2):
    draw = ImageDraw.Draw(img)

    # four edges: [top, left, bottom, right]
    xy_list = [
        ((0, 0), (img.size[0], 0)),
        ((0, 0), (0, img.size[1])),
        ((0, img.size[1] - 2), (img.size[0], img.size[1] - 2)),
        ((img.size[0] - 2, 0), (img.size[0] - 2, img.size[1])),
    ]
    for xy in xy_list:
        log('drawing a line between %s and %s' % xy)
        draw.line(xy, fill=fill, width=width)


def bocho(fname, pages=None, width=None, height=None, offset_x=None,
          offset_y=None, spacing=None, zoom=None, angle=None, affine=False,
          reverse=False):
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
    x_spacing = spacing
    y_spacing = 0

    if angle:
        y_spacing = spacing * math.cos(angle)
        x_spacing = abs(y_spacing / math.tan(angle))

    log('spacing: %s' % str((x_spacing, y_spacing)))

    page_images = [
        Image.open(_slice_page(fname, x - 1)).convert('RGB')
        for x in pages
    ]

    # Calculate the aspect ratio of the input document from the first page in
    # the list
    page_size = page_images[0].size
    aspect = float(page_size[0]) / float(page_size[1])
    log('input document aspect ratio: 1:%s' % (1 / aspect))

    # We make a bit of an assumption here that the output image is going to be
    # wider than it is tall and that by default we want the sliced pages to fit
    # vertically (assuming no rotation) and that the spacing will fill the
    # image horizontally.
    page_height = px(height * zoom)
    page_width = page_height * aspect

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
            px((page_width * n) - (page_width - x_spacing) * (n - 1)),
            px(page_height + max(y_coords))
        )

    outfile = Image.new('RGB', size)

    log('output size before rotating: %s' % str(size))

    for x, img in enumerate(reversed(page_images), 1):
        # Draw lines down the right and bottom edges of each page to provide
        # visual separation. Cheap drop-shadow basically.
        _add_border(img)

        img = img.resize((px(page_width), page_height), Image.ANTIALIAS)

        if reverse:
            coords = (x_coords[x - 1], y_coords[x - 1])
        else:
            coords = (x_coords[-x], y_coords[-x])
        log('placing page %d at %s' % (pages[-x], coords))
        outfile.paste(img, coords)

    if angle != 0:
        if affine:
            outfile = outfile.transform(
                (px(outfile.size[0] * 1.5), outfile.size[1]),
                Image.AFFINE,
                (1, -0.5, 0, 0, 1, 0),
                Image.BICUBIC,
            )

        outfile = outfile.rotate(math.degrees(angle), Image.BILINEAR, True)
        log('output size before cropping: %s' % str(outfile.size))

        # Rotation is about the center (and expands to fit the result), so
        # cropping is simply a case of positioning a rectangle of the desired
        # width & height about the center of the rotated image.
        left = px((outfile.size[0] - width) / 2) - offset_x
        top = px((outfile.size[1] - height) / 2) - offset_y
        outfile = outfile.crop((left, top, left + width, top + height))

    outfile.save(file_path)
    return file_path


if __name__ == '__main__':
    global VERBOSE

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
        '--reverse', action='store_true', default=False,
    )
    parser.add_argument(
        '--affine', action='store_true', default=False,
    )
    parser.add_argument(
        '--verbose', action='store_true', default=False,
    )
    parser.add_argument('--pages', type=int, nargs='*')
    parser.add_argument('pdf_file')
    args = parser.parse_args()

    if not args.pdf_file[-4:] == '.pdf':
        raise Exception("Input file doesn't look like a PDF")

    VERBOSE = args.verbose

    print bocho(
        args.pdf_file, args.pages, args.width, args.height,
        args.offset_x, args.offset_y, args.spacing,
        args.zoom, args.angle, args.affine, args.reverse,
    )
