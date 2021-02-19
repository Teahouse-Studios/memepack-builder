from .error_code import *
from argparse import ArgumentParser
import os


def verify_args(args, log):
    for k in ('platform', 'type', 'output', 'hash'):
        if k not in args:
            _raise_error(ERR_MISSING_ARGUMENT,
                         f'Missing required argument "{k}".', log)
            return False
    return True


def generate_parser():
    parser = ArgumentParser(prog='memepack_builder',
                            description='Build memefied Minecraft resource pack')
    parser.add_argument('platform', default='je', choices=(
        'je', 'be'), help='Which platform the pack is targeting. Should be "je" or "be". Default value is "je".')
    parser.add_argument('type', default='normal', choices=('normal', 'compat', 'legacy', 'mcpack', 'zip'),
                        help='Build type. Depending on "platform" argument, this argument takes different values. For "je", "normal", "compat" and "legacy" are accepted; for "be", "mcpack" and "zip" are accepted. When is "legacy", implies "--format 3".')
    parser.add_argument('-r', '--resource', nargs='*', default='all',
                        help="(Experimental) Include resource modules. Should be module names, 'all' or 'none'. Defaults to 'all'.")
    parser.add_argument('-l', '--language', nargs='*', default='none',
                        help="(Experimental) Include language modules. Should be module names, 'all' or 'none'. Defaults to 'none'.")
    parser.add_argument('-x', '--mixed', nargs='*', default='none',
                        help="(Experimental) Include mixed modules. Should be module names, 'all' or 'none'. Defaults to 'none'.")
    parser.add_argument('-s', '--sfw', action='store_true',
                        help="Use 'suitable for work' strings, equals to '--language sfw'.")
    parser.add_argument('-c', '--collection', nargs='*', default='none',
                        help="(Experimental) Include module collections. Should be module names, 'all' or 'none'. Defaults to 'none'.")
    parser.add_argument('-m', '--mod', nargs='*', default='none',
                        help="(JE only)(Experimental) Include mod string files. Should be file names in 'mods/' folder, 'all' or 'none'. Defaults to 'none'. Pseudoly accepts a path, but only files in 'mods/' work.")
    parser.add_argument('-f', '--format', type=int,
                        help='(JE only) Specify "pack_format". When omitted, will default to 3 if build type is "legacy" and 7 if build type is "normal" or "compat". A wrong value will cause the build to fail.')
    parser.add_argument('-p', '--compatible', action='store_true',
                        help="(BE only) Make the pack compatible to other addons. This will generate only one language file 'zh_CN.lang'.")
    parser.add_argument('-o', '--output', nargs='?', default='builds',
                        help="Specify the location to output packs. Default location is 'builds/' folder.")
    parser.add_argument('--hash', action='store_true',
                        help="Add a hash into file name.")
    return parser


def process_args(args):
    module_types = ('resource', 'language', 'mixed', 'collection')
    args['modules'] = {key: args.pop(key) for key in module_types}
    if args['sfw'] and 'sfw' not in args['modules']['language']:
        args['modules']['language'].append('sfw')
    return args


def build(args):
    log = []
    warning_count = 0
    if not verify_args(args, log):
        return _build_msg(ERR_MISSING_ARGUMENT, warning_count, '', log)
    from ..ModuleChecker import ModuleChecker
    from ..PlatformChecker import PlatformChecker
    curdir = os.getcwd()
    main_res_path = os.path.join(curdir, "meme_resourcepack")
    checker = ModuleChecker(os.path.join(curdir, "modules"))
    checker.check_module()
    log.extend(checker.check_log)
    warning_count += checker.warning_count
    if args['platform'] == 'je':
        if args['type'] in ('mcpack', 'zip'):
            _raise_error(ERR_MISMATCHED_ARGUMENT,
                         f'Platform "JE" detected but received "{args["type"]}" type.', log)
            return _build_msg(ERR_MISMATCHED_ARGUMENT, warning_count, '', log)
        from ..JEPackBuilder import JEPackBuilder
        builder = JEPackBuilder(main_res_path, checker.module_info, os.path.join(
            curdir, "mods"), os.path.join(curdir, "mappings"))
    elif args['platform'] == 'be':
        if args['type'] in ('normal', 'compat', 'legacy'):
            _raise_error(ERR_MISMATCHED_ARGUMENT,
                         f'Platform "BE" detected but received "{args["type"]}" type.', log)
            return _build_msg(ERR_MISMATCHED_ARGUMENT, warning_count, '', log)
        from ..BEPackBuilder import BEPackBuilder
        builder = BEPackBuilder(main_res_path, checker.module_info)
    else:
        _raise_error(ERR_UNKNOWN_PLATFORM,
                     f'Unknown platform "{args["platform"]}".')
        return _build_msg(ERR_UNKNOWN_PLATFORM, warning_count, '', log)
    msg = PlatformChecker(main_res_path, args['platform']).check()
    if msg['code'] != ERR_OK:
        _raise_error(msg['code'], msg['message'], log)
        return _build_msg(msg['code'], warning_count, '', log)
    else:
        builder.build_args = args
        builder.build()
        log.extend(builder.build_log)
        warning_count += builder.warning_count
        return _build_msg(builder.error_code, warning_count, builder.file_name, log)


def _build_msg(err_code: int, warning_count: int, file_name: str, log: list):
    return {
        'error_code': err_code,
        'warning_count': warning_count,
        'file_name': file_name,
        'log': log
    }


def _raise_error(err_code: int, msg: str, log: list):
    log.append(f'Error [{err_code}]: {msg}')
