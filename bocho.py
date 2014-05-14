#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import math
import os
import shlex
import subprocess
import tempfile

from PIL import Image

try:
    import wand
    WAND_AVAILABLE = True
except ImportError:
    WAND_AVAILABLE = False

DEFAULTS = {
    'pages': range(1, 6),
    'width': 630,  # pixels
    'height': 290,  # pixels
    'angle': 0,  # degrees anti-clockwise from vertical
    'offset': (0, 0),  # pixels
    'spacing': (107, 0),  # pixels
    'zoom': 1.0,
    'border': 2,  # pixels
    'shadow': False,
    'affine': False,
    'reverse': False,
    'reuse': False,
    'delete': False,
    'resolution': 300,  # dpi
}

VERBOSE = False


def log(msg):
    if VERBOSE:
        print msg


def px(number):
    # Round a float & make it a valid pixel value. More accurate than just int.
    return int(round(number))


def slice_pages(fname, pages, out_path=None, resolution=300, use_convert=True):
    """Use ImageMagick to slice the PDF into individual PNG pages.

    For example::

        >>> from bocho import slice_pages
        >>> pngs = slice_pages('/path/to/my-file.pdf', [1,2,3])
        >>> print pngs
        [
            '/path/to/my-file-Gq_Yw1-1.png',
            '/path/to/my-file-Gq_Yw1-2.png',
            '/path/to/my-file-Gq_Yw1-3.png',
        ]

    If ``out_path`` isn't provided, we use the :mod:`tempfile` module to
    generate one.

    Args:
        fname (str): The PDF to split
        pages (list): Pages to slice

    Kwargs:
        out_path (str): Output file name format (passed to ImageMagick)
        resolution (int): Required DPI (passed to ImageMagick)
        use_convert (bool): If False, we use Wand (if available)

    Returns:
        list: Paths to page PNG files

    """
    if not out_path:
        prefix = '%s-' % fname[:-4]
        fd, out_path = tempfile.mkstemp(prefix=prefix, suffix='.png')
        os.close(fd)
        os.remove(out_path)

    fname = '%s[%s]' % (fname, ','.join(str(x - 1) for x in pages))

    if use_convert or not WAND_AVAILABLE:
        command = "convert -density %d '%s' %s"
        command = command % (resolution, fname, out_path)
        sh_args = shlex.split(str(command))
        ret = subprocess.call(sh_args)
        if ret > 0:
            raise Exception('Non-zero return code: "%s"' % command)
    else:
        from wand import image
        page_image_files = image.Image(
            filename=fname,
            resolution=resolution,
        )
        with page_image_files.convert('png') as f:
            f.save(filename=out_path)

    return glob.glob('%s*' % out_path[:-4])


def _add_border(img, fill='black', width=2, shadow=False):
    if not width or width < 0:
        return img

    log('drawing borders on a page %dx%d' % img.size)
    new_img = Image.new(
        'RGBA', (img.size[0] + width * 2, img.size[1] + width * 2), fill,
    )

    def _pixel_in_border(x, y):
        return (
            y < width
            or x < width
            or y > img.size[1] + width
            or x > img.size[0] + width
        )

    def _pixel_in_outer_border(x, y):
        return (
            y < width / 2
            or x < width / 2
            or y > img.size[1] + width * 1.5
            or x > img.size[0] + width * 1.5
        )

    if shadow:
        # Here, we split the black border into two equal parts - inner and
        # outer - and make the outer one translucent and the inner one slightly
        # less translucent. The net effect is to soften the borders a bit.
        p = new_img.load()
        for y in range(new_img.size[1]):
            for x in range(new_img.size[0]):
                pixel = list(p[x, y])
                if _pixel_in_border(x, y):
                    # Outer border is slightly more translucent than the inner
                    if _pixel_in_outer_border(x, y):
                        pixel[3] = 100
                        p[x, y] = tuple(pixel)
                    else:
                        pixel[3] = 140
                        p[x, y] = tuple(pixel)
    else:
        # If we're not adding a shadow effect, we just ditch the alpha layer
        # and make the background pure black.
        new_img.putalpha(255)

    new_img.paste(img, (width, width), img)

    return new_img


def bocho(fname, **kwargs):
    """Slice the given file name into page thumbnails and arrange as a preview.

    The only required information is the path to the input file, all other
    parameters have sensible defaults (see ``bocho.DEFAULTS``).

    Per-page PNG files can optionally be re-used between runs, but the output
    file must be removed or we will raise an exception unless you pass
    ``delete=True``.

    Args:
        fname (str): The input file name

    Kwargs:
        pages (list): Pages to use from the source file
        width (int): pixel width of the output image
        height (int): pixel height of the output image
        resolution (int): DPI used in converting PDF pages to PNG
        angle (int): rotation from vertical (degrees between -90 and 90)
        offset (tuple): two-tuple of pixel offsets for shifting the output
        spacing (tuple): two-tuple of pixel spacing between pages
        zoom: (tuple) zoom factor to be applied after arranging pages
        border (int): pixel width of the page border to be added
        shadow (bool): soften the border for a 'shadow' effect (slow)
        affine (bool): optionally apply a subtle affine transformation
        reverse (bool): stack the pages right to left
        reuse (bool): re-use the per-page PNG files between runs
        delete (bool): delete the output file before running
        use_convert (bool): optionally use 'convert' rather than Wand

    Returns:
        string. The path to the output file

    """
    def _kwarg_or_default(name):
        result = kwargs.get(name)
        if result is None:
            result = DEFAULTS.get(name)
        return result

    pages = _kwarg_or_default('pages')
    width = _kwarg_or_default('width')
    height = _kwarg_or_default('height')
    resolution = _kwarg_or_default('resolution')
    angle = _kwarg_or_default('angle')
    offset = _kwarg_or_default('offset')
    spacing = _kwarg_or_default('spacing')
    zoom = _kwarg_or_default('zoom')
    border = _kwarg_or_default('border')
    shadow = _kwarg_or_default('shadow')
    affine = _kwarg_or_default('affine')
    reverse = _kwarg_or_default('reverse')
    reuse = _kwarg_or_default('reuse')
    delete = _kwarg_or_default('delete')
    use_convert = _kwarg_or_default('use_convert')

    if not use_convert and not WAND_AVAILABLE:
        log('Wand is not installed, so using `convert` directly.')
        use_convert = True

    assert -90 <= angle <= 90

    angle = math.radians(angle)

    file_path = '%s-bocho-%sx%s.png' % (fname[:-4], width, height)
    if os.path.exists(file_path):
        if not delete:
            raise Exception("%s already exists, not overwriting" % file_path)
        else:
            log('removing output file before running: %s' % file_path)
            os.remove(file_path)

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
            if delete:
                for path in tmp_image_names:
                    if os.path.exists(path):
                        os.remove(path)
            else:
                raise Exception(
                    'Not overwriting page PNG files, please delete: %s' %
                    tmp_image_names,
                )
        log('converting input PDF to individual page PDFs')
        slice_pages(fname, pages, out_path, resolution, use_convert)

    page_0 = Image.open(tmp_image_names[0])
    log('page size of sliced pages: %dx%d' % page_0.size)

    slice_size = page_0.size
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

    for x, tmp in enumerate(reversed(tmp_image_names), 1):
        # Draw lines down the right and bottom edges of each page to provide
        # visual separation. Cheap drop-shadow basically.
        img = Image.open(tmp)
        img.putalpha(255)
        img = _add_border(img, width=border, shadow=shadow)

        if reverse:
            coords = (x_coords[x - 1], y_coords[x - 1])
        else:
            coords = (x_coords[-x], y_coords[-x])

        # If we don't use img as the mask, PIL drops the alpha channel
        log('placing page %d at %s' % (pages[-x], coords))
        outfile.paste(img, coords, img)

    del page_0, img

    if reuse:
        log('leaving individual page PNG files in place')
    else:
        for tmp in tmp_image_names:
            log('deleting temporary file: %s' % tmp)
            os.remove(tmp)

    if affine:
        log('applying affine transformation')
        # Currently we just apply a non-configurable, subtle transform
        outfile = outfile.transform(
            (px(outfile.size[0] * 1.3), outfile.size[1]),
            Image.AFFINE,
            (1, -0.3, 0, 0, 1, 0),
            Image.BICUBIC,
        )

    if angle != 0:
        log('rotating image by %0.2f degrees' % math.degrees(angle))
        outfile = outfile.rotate(math.degrees(angle), Image.BICUBIC, True)
        log('output size before cropping: %dx%d' % outfile.size)

    # Cropping is simply a case of positioning a rectangle of the desired
    # dimensions about the center of the image.
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
    parser.add_argument('--reverse', action='store_true')
    parser.add_argument('--border', type=int, nargs='?')
    parser.add_argument('--shadow', action='store_true')
    parser.add_argument('--affine', action='store_true')
    parser.add_argument('--use_convert', action='store_true')
    parser.add_argument(
        '--reuse', action='store_true',
        help='Re-use page PNG files between runs. If True, you need to clear '
             'up after yourself, but multiple runs on the same input will be '
             'much faster.',
    )
    parser.add_argument(
        '--delete', action='store_true',
        help='Delete the output file before running. If False, and the file '
             'exists, an exception will be raised and nothing will happen.',
    )
    parser.add_argument('--verbose', action='store_true', default=False)
    args = parser.parse_args()

    if not args.pdf_file[-4:] == '.pdf':
        raise Exception("Input file doesn't look like a PDF")

    VERBOSE = args.verbose

    kwargs = dict(args._get_kwargs())
    offset = (
        kwargs.pop('offset_x') or DEFAULTS.get('offset')[0],
        kwargs.pop('offset_y') or DEFAULTS.get('offset')[1]
    )
    spacing = (
        kwargs.pop('spacing_x') or DEFAULTS.get('spacing')[0],
        kwargs.pop('spacing_y') or DEFAULTS.get('spacing')[1]
    )

    print bocho(args.pdf_file, offset=offset, spacing=spacing, **kwargs)
