#!/usr/bin/env python3
"""news-image-20261122 — entry point.

The poster itself lives in this repository as entry.png (rendered by
build_poster.py, a PIL script run at authoring time). All this program does
is copy that image into the output directory, as the competition kit
explicitly allows: a repository holding the image plus a one-line program
that copies it there.

Standard library only. No network, no clock, no randomness: the output is
byte-identical to the stored image on every run.
"""

import os
import shutil
import sys

IMAGE_NAME = "entry.png"


def image_path():
    """Absolute path of the poster stored next to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, IMAGE_NAME)


def output_dir():
    """Where the harness expects the entry; /output unless overridden."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    src = image_path()
    if not os.path.isfile(src):
        print("missing image: %s" % src, file=sys.stderr)
        return 1
    dest_dir = output_dir()
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, IMAGE_NAME)
    shutil.copyfile(src, dest)
    print("wrote %s (%d bytes)" % (dest, os.path.getsize(dest)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
