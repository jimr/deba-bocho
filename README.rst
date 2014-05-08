==========
Deba bōchō
==========

Slice up PDFs like a pro::

    % python bocho.py my-fancy-file.pdf --pages 1 3 5 6 10 --angle 30 --zoom 1.6
    my-fancy-file-bocho-630x290.png

``bocho`` takes a PDF file and creates a "stacked page" preview from a selection of pages.

It accepts a bunch of options for customising the output (pass the ``-h`` flag for details).

Installation
============

Requires ImageMagick and the contents of ``requirements.txt``, e.g::

    % sudo apt-get install imagemagick
    % pip install -r requirements.txt

On OS X, it's a bit more complicated::

    % brew install ghostscript
    % brew install imagemagick
    % ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install --allow-external pyPdf --allow-unverified pyPdf -r requirements.txt


TODO
====

Pretty much everything.

- implement rotation properly ✓
- allow a "zoom" option ✓
- optional drop-shadows (and make right-edge black separators optional also)
- automatic spacing as an option as well as fixed pixel spacing
- horizontal and vertical spacing (currently only horizontal)
- horizontal and vertical offsets ✓
- optional right-to-left stacking
- handle non-A4 aspect ratio input documents ✓
- ensure sliced PNGs are large enough when custom width / height are specified
- docs
