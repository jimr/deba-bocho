#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image

from bocho.utils import px


def shear(img, x=False, y=False):
    """Apply vertical or horizontal shear effects (or both).

    We achieve this by applying a simple affine transformation.

    The new image size calculation is a bit off if you apply both horizontal
    and vertical shear at the same time.

    """
    # If true, then this is a no-op so let's just not bother
    if not x and not y:
        return img

    width, height = img.size
    x_shift = abs(x) * height
    y_shift = abs(y) * width
    
    # If we're applying a positive shear in either direction, we must also
    # apply a translation (by setting the 'c' and 'f' parameters passed to
    # PIL) so the resulting image data ends up entirely inside the bounds of
    # the resized image.
    # If we don't do this we'll end up with an output image of the correct
    # size but leaving parts of the original chopped off.
    return img.transform(
        (width + px(x_shift), height + px(y_shift)),
        Image.AFFINE,
        (
            1, x, -x_shift if x > 0 else 0,
            y, 1, -y_shift if y > 0 else 0,
        ),
        Image.BICUBIC,
    )
