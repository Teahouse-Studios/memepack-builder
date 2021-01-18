import sys
from memepack_builder._internal.cli import build, generate_parser, process_args


def _log_highlight(entry: str):
    if entry.startswith('Warning'):
        return f'\033[33m{entry}\033[0m'
    elif entry.startswith('Error'):
        return f'\033[1;31m{entry}\033[0m'
    else:
        return entry


def _log_filter(entry: str):
    return sys.stderr if entry.startswith('Warning') or entry.startswith('Error') else sys.stdout


def main(args=None, highlight=None):
    if not args:
        args = process_args(vars(generate_parser().parse_args()))
    result = build(args)
    log = result['log']
    if highlight:
        log = map(_log_highlight, result['log'])
    for entry in log:
        print(entry, file=_log_filter(entry))
    return result
