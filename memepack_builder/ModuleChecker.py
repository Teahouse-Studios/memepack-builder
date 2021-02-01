__all__ = ['ModuleChecker']

import json
import os
from memepack_builder._internal.logger import logger
from memepack_builder._internal.common import _build_message
from memepack_builder._internal.err_code import *


class ModuleChecker(object):
    def __init__(self, module_path: str):
        self.__module_path = module_path
        self.__logger = logger()
        self.clean_status()

    @property
    def check_log(self):
        return self.__logger.raw_log

    @property
    def module_info(self):
        if not self.__checked:
            self.check_module()
        return self.__module_info

    @property
    def module_path(self):
        return self.__module_path

    @property
    def warning_count(self):
        return self.__warning_count

    @module_path.setter
    def module_path(self, value: str):
        self.__module_path = value

    def clean_status(self):
        self.__checked = False
        self.__module_info = {}
        self.__warning_count = 0
        self.__logger.clear()

    def check_module(self):
        self.clean_status()
        module_info = {
            'path': self.module_path,
            'modules': {
                'language': [],
                'resource': [],
                'mixed': [],
                'collection': []
            }
        }
        for module in os.listdir(self.module_path):
            result = _analyze_module(
                os.path.join(self.module_path, module))
            if result['code'] == WARN_OK:
                module_info['modules'][result['data'].pop(
                    'type')].append(result['data'])
            else:
                entry = f"Warning [{result['code']}]: {result['message']}"
                self.__logger.append(entry)
                self.__warning_count += 1
        self.__module_info = module_info
        self.__checked = True


def _analyze_module(path: str):
    manifest = os.path.join(path, "module_manifest.json")
    dir_name = os.path.basename(path)
    if os.path.exists(manifest) and os.path.isfile(manifest):
        data = json.load(open(manifest, 'r', encoding='utf8'))
        for key in ('name', 'type', 'description'):
            if key not in data:
                return _result_msg(WARN_BROKEN_MODULE, f'In path "{dir_name}": Incomplete module_manifest.json, missing "{key}" field.')
        if data['type'] in ('language', 'mixed'):
            if not (os.path.exists(os.path.join(path, "add.json")) or os.path.exists(os.path.join(path, "remove.json"))):
                return _result_msg(WARN_BROKEN_MODULE, f'In path "{dir_name}": Expected a language module, but couldn\'t find "add.json" or "remove.json".')
        elif data['type'] == 'resource':
            pass
        elif data['type'] == 'collection':
            if 'contains' not in data:
                return _result_msg(WARN_BROKEN_MODULE, f'In path "{dir_name}": Expected a module collection, but "contains" key is missing in module_manifest.json.')
            else:
                if 'collection' in data['contains']:
                    return _result_msg(WARN_LOOP_COLLECTION, f'In path "{dir_name}": Try to contain another collection in a collection.')
        else:
            return _result_msg(WARN_UNKNOWN_MODULE, f'In path "{dir_name}": Unknown module type "{data["type"]}".')
        data['dirname'] = dir_name
        return _result_msg(WARN_OK, "Analysis successfully finished.", data)
    else:
        return _result_msg(WARN_BROKEN_MODULE, f'In path "{dir_name}": No module_manifest.json.')


def _result_msg(code: int, message: str, data=None):
    result = _build_message(code, message)
    if data:
        result['data'] = data
    return result
