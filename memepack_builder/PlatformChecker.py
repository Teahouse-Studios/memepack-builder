__all__ = ['PlatformChecker']

import os
from memepack_builder._internal.error_code import *


class PlatformChecker(object):
    def __init__(self, main_res_path: str, intended_platform: str):
        self.__main_res_path = main_res_path
        self.__intended = intended_platform
        self.__real = ''

    def check(self):
        je_target = os.path.join(self.__main_res_path, "assets")
        be_target = os.path.join(self.__main_res_path, "manifest.json")
        if os.path.exists(je_target) and os.path.isdir(je_target):
            self.__real = 'je'
        elif os.path.exists(be_target) and os.path.isfile(be_target):
            self.__real = 'be'
        else:
            return _build_message(ERR_UNKNOWN_PLATFORM, 'Unknown target platform.')
        if self.__real != self.__intended:
            return _build_message(ERR_MISMATCHED_PLATFORM, f'{self.__real.upper()} structure detected, can\'t build {self.__intended.upper()} pack.')
        else:
            return _build_message(ERR_OK, 'Check passed.')


def _build_message(code: int, message: str):
    return {'code': code, 'message': message}
