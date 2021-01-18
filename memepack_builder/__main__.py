import os
import sys

if __package__ == '':
    path = os.path.dirname(__file__)
    if path not in sys.path:
        sys.path.insert(0, path)

from .wrapper import main as _main
if __name__ == '__main__':
    sys.exit(_main(highlight=True)['error_code'])
