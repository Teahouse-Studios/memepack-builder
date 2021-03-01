import sys
from memepack_builder._internal.cli import build, generate_parser, process_args


def _log_highlight(log: list, highlight: bool):
    for entry in log:
        if entry.startswith('Warning'):
            yield highlight and f'\033[33m{entry}\033[0m' or entry, sys.stderr
        elif entry.startswith('Error'):
            yield highlight and f'\033[1;31m{entry}\033[0m' or entry, sys.stderr
        else:
            yield entry, sys.stdout


def main(args=None, highlight=True):
    if not args:
        args = process_args(vars(generate_parser().parse_args()))
    result = build(args)
    for entry, output in _log_highlight(result['log'], highlight):
        print(entry, file=output)
    return result
