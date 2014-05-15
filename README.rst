==========
Deba bōchō
==========

Slice up PDFs like a pro::

    % bocho my-fancy-file.pdf --pages 1 3 5 6 10 --angle 30 --zoom 1.6
    my-fancy-file-bocho-630x290.png

Takes a PDF file and creates a "stacked page" preview from a selection of pages.

It accepts a bunch of options for customising the output (pass the ``-h`` flag for details).

Installation
============

Requires ImageMagick so you might need to, e.g::

    % sudo apt-get install imagemagick

If you want to use ``Wand`` instead of calling ``convert`` directly, you'll also need to perform some some additional steps, e.g::

    % sudo apt-get install libmagickwand-dev
    % pip install wand

See their installation instructions for more details.

On OS X, you'll want to use Homebrew to get the low-level dependencies in place::

    % brew install ghostscript imagemagick

Once all that's sorted, you just need to ``pip install deba-bocho``.

Usage
=====

For information on usage, run ``bocho --help``. If you want to use it as a module::

   >>> import bocho
   >>> help(bocho.assemble)

Configuration
=============

If you will be using the same options many times, it's probably worth creating a preset in a ``config.ini`` file (see config.example.ini_ or the example below to get started).

.. _config.example.ini: https://github.com/jimr/deba-bocho/blob/master/config.example.ini

By default, ``bocho`` will check for ``$HOME/.config/bocho/config.ini``, so it's probably best to keep your config there, but you can pass the ``--config`` option with the path to an alternative location.

.. code-block:: ini

    [example]
    pages = 1,3,5,7,9
    width = 630
    height = 290
    border = 4
    reuse = true
    delete = true
    verbose = true
    use_convert = true

You can tell ``bocho`` to use this preset by calling::

    bocho /path/to/file.pdf --preset example [--config /path/to/config.ini]

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
- use proper logging
