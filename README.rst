==========
Deba bōchō
==========

Slice up PDFs like a pro::

    % python bocho.py my-fancy-file.pdf --pages 1 3 5 6 10 --angle 30 --zoom 1.6
    my-fancy-file-bocho-630x290.png

Takes a PDF file and creates a "stacked page" preview from a selection of pages.

It accepts a bunch of options for customising the output (pass the ``-h`` flag for details).

Installation
============

``pip install deba-bocho``.

Requires ImageMagick so you might need to, e.g::

    % sudo apt-get install imagemagick

If you want to use ``Wand`` instead of calling ``convert`` directly, you'll also need to perform some some additional steps, e.g::

    % sudo apt-get install libmagickwand-dev
    % pip install wand

See their installation instructions for more details.

On OS X, you'll want to use Homebrew to get the low-level dependencies in place::

    % brew install ghostscript imagemagick

TODO
====

- implement rotation properly ✓
- allow a "zoom" option ✓
- optional drop-shadows ✓
- make shadows smarter in their orientation (they're currently uniform, not respecting the angle / affine transformation)
- make the basic edge separators optional ✓
- automatic spacing as an option as well as fixed pixel spacing
- horizontal and vertical spacing ✓
- horizontal and vertical offsets ✓
- optional right-to-left stacking ✓
- handle non-A4 aspect ratio input documents ✓
- optionally apply transforms:

  - affine ✓ (basic, subtle, non-configurable)
  - perspective

- ensure sliced PNGs are large enough when custom width / height are specified
- fix x and y spacing calculation to account for any applied rotation & transformation
- allow transforms to be configurable (probably with presets defined in an ``.ini`` file)
- drop the PyPDF dependency ✓
- use an ImageMagick binding rather than using ``subprocess`` to call ``convert`` ✓ (Wand)
- optionally re-use pages between runs ✓
- allow user-specified resolution for the PDF to PNG conversion ✓
- docs ✓
- pretty pictures illustrating the effect of the various options
