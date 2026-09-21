#!/usr/bin/env python3
"""
telespotx - compatibility shim.

telespotx's parallel httpx engine is now built into telespot.py (v6.0.0),
which runs every engine concurrently per format and paces each engine by
its own limits. This shim keeps old commands working by running

    telespot.py --mode fast <your arguments>

Use telespot.py directly; see `telespot.py --help` for --mode fast/balanced/safe.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import telespot  # noqa: E402

VERSION = telespot.VERSION


def main():
    argv = sys.argv[1:]
    print("telespotx has merged into telespot.py; running: telespot.py --mode fast " + " ".join(argv))
    if '--mode' not in argv and '--fast' not in argv and '--safe' not in argv:
        argv = ['--mode', 'fast'] + argv
    return telespot.main(argv)


if __name__ == '__main__':
    sys.exit(main())
