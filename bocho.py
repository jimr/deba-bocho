#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import math
import os

from PIL import Image
from wand.image import Image as WandImage

DEFAULTS = {
    'pages': range(1, 6),
    'width': 630,  # pixels
    'height': 290,  # pixels
    'angle': 0,  # degrees anti-clockwise from vertical
    'offset': (0, 0),  # pixels
    'spacing': (107, 0),  # pixels
    'zoom': 1.0,
}

VERBOSE = False


def log(msg):
    if VERBOSE:
        print msg


def px(number):
    # Round a float & make it a valid pixel value. More accurate than just int.
    return int(round(number))


def _add_border(img, fill='black', width=2):
    log('drawing borders on a page %dx%d' % img.size)
    border_background = Image.new(
        'RGBA', (img.size[0] + width, img.size[1] + width), color=fill,
    )
    border_background.paste(img, (width, width))

    return border_background


def bocho(fname, pages=None, width=None, height=None, offset=None,
          spacing=None, zoom=None, angle=None, affine=False, reverse=False,
          reuse=False):
    pages = pages or DEFAULTS.get('pages')
    width = width or DEFAULTS.get('width')
    height = height or DEFAULTS.get('height')
    angle = angle or DEFAULTS.get('angle')
    offset = offset or DEFAULTS.get('offset')
    spacing = spacing or DEFAULTS.get('spacing')
    zoom = zoom or DEFAULTS.get('zoom')

    assert -90 <= angle <= 90

    angle = math.radians(angle)

    file_path = '%s-bocho-%sx%s.png' % (fname[:-4], width, height)
    if os.path.exists(file_path):
        raise Exception("%s already exists, not overwriting" % file_path)

    n = len(pages)
    x_spacing, y_spacing = spacing

    if angle:
        y_spacing = x_spacing * math.cos(angle)
        x_spacing = abs(y_spacing / math.tan(angle))

    log('spacing: %s' % str((x_spacing, y_spacing)))

    out_path = '%s-page.png' % fname[:-4]
    tmp_image_names = ['%s-%d.png' % (out_path[:-4], p - 1) for p in pages]

    if all(map(os.path.exists, tmp_image_names)) and reuse:
        log('re-using existing individual page PNGs')
    else:
        if any(map(os.path.exists, tmp_image_names)):
            raise Exception(
                'Error: not overwriting page PNG files, please delete: %s' %
                tmp_image_names,
            )
        log('converting input PDF to individual page PDFs')
        page_image_files = WandImage(
            filename='%s[%s]' % (fname, ','.join(str(x - 1) for x in pages)),
            resolution=300,
        )
        with page_image_files.convert('png') as f:
            f.save(filename=out_path)

    page_images = []
    for tmp in tmp_image_names:
        page_images.append(Image.open(tmp))

    log('page size of sliced pages: %dx%d' % page_images[0].size)

    slice_size = page_images[0].size
    scale = slice_size[1] / height
    log('input to output scale: %0.2f' % scale)

    x_spacing = px(x_spacing * scale)
    y_spacing = px(y_spacing * scale)
    log('spacing after scaling up: %dx%d' % (x_spacing, y_spacing))

    # We make a bit of an assumption here that the output image is going to be
    # wider than it is tall and that by default we want the sliced pages to fit
    # vertically (assuming no rotation) and that the spacing will fill the
    # image horizontally.
    page_width = px(slice_size[0])
    page_height = px(slice_size[1])
    log('page size before resizing down: %dx%d' % (page_width, page_height))

    # If there's no angle specified then all the y coords will be zero and the
    # x coords will be a multiple of the provided spacing
    x_coords = map(int, [i * x_spacing for i in range(n)])
    y_coords = map(int, [i * y_spacing for i in range(n)])

    if angle < 0:
        y_coords.sort(reverse=True)

    size = (px(width * scale), px(height * scale))
    log('output size before resizing: %dx%d' % size)
    if angle != 0:
        # If we're rotating the pages, we stack them up with appropriate
        # horizontal and vertical offsets first, then we rotate the result.
        # Because of this, we must expand the output image to be large enough
        # to fit the unrotated stack. The rotation operation below will expand
        # the output image enough so everything still fits, but this bit we
        # need to figure out for ourselves in advance.
        size = (
            page_width + (n - 1) * x_spacing,
            page_height + max(y_coords)
        )
        log('output size before rotate + crop: %dx%d' % size)

    outfile = Image.new('RGB', size)
    log('outfile dimensions: %dx%d' % outfile.size)

    for x, img in enumerate(reversed(page_images), 1):
        # Draw lines down the right and bottom edges of each page to provide
        # visual separation. Cheap drop-shadow basically.
        img = _add_border(img)

        if reverse:
            coords = (x_coords[x - 1], y_coords[x - 1])
        else:
            coords = (x_coords[-x], y_coords[-x])
        log('placing page %d at %s' % (pages[-x], coords))
        outfile.paste(img, coords)

    if reuse:
        log('leaving individual page PNG files in place')
    else:
        for tmp in tmp_image_names:
            log('deleting temporary file: %s' % tmp)
            os.remove(tmp)

    if angle != 0:
        if affine:
            log('applying affine transformation')
            # Currently we just apply a non-configurable, subtle transform
            outfile = outfile.transform(
                (px(outfile.size[0] * 1.3), outfile.size[1]),
                Image.AFFINE,
                (1, -0.3, 0, 0, 1, 0),
                Image.BICUBIC,
            )

        log('rotating image by %0.2f degrees' % math.degrees(angle))
        outfile = outfile.rotate(math.degrees(angle), Image.BICUBIC, True)
        log('output size before cropping: %dx%d' % outfile.size)

        # Rotation is about the center (and expands to fit the result), so
        # cropping is simply a case of positioning a rectangle of the desired
        # dimensions about the center of the rotated image.
        delta = map(px, ((width * scale) / zoom, (height * scale) / zoom))
        left = (outfile.size[0] - delta[0]) / 2 - (offset[0] * scale)
        top = (outfile.size[1] - delta[1]) / 2 - (offset[1] * scale)
        box = (left, top, left + delta[0], top + delta[1])

        outfile = outfile.crop(box)
        log('crop box: (%d, %d, %d, %d)' % box)

    # Finally, resize the output to the desired size and save.
    outfile = outfile.resize((width, height), Image.ANTIALIAS)
    log('output saved with dimensions: %dx%d' % outfile.size)
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
        '--offset_x', type=int, nargs='?', default=DEFAULTS.get('offset')[0],
    )
    parser.add_argument(
        '--offset_y', type=int, nargs='?', default=DEFAULTS.get('offset')[1],
    )
    parser.add_argument(
        '--spacing_x', type=int, nargs='?', default=DEFAULTS.get('spacing')[0],
    )
    parser.add_argument(
        '--spacing_y', type=int, nargs='?', default=DEFAULTS.get('spacing')[1],
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
        '--reuse', action='store_true', default=False,
        help='Re-use page PNG files between runs. If True, you need to clear '
             'up after yourself, but multiple runs on the same input will be '
             'much faster.',
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
        (args.offset_x, args.offset_y), (args.spacing_x, args.spacing_y),
        args.zoom, args.angle, args.affine, args.reverse, args.reuse,
    )
