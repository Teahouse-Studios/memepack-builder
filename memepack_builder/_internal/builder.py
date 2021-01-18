__all__ = [
    'builder'
]

import json
import os
from .common import _build_message
from .err_code import *
from .logger import logger
from hashlib import sha256

_keys = 'platform', 'type', 'modules', 'mod', 'output', 'hash', 'format', 'compatible'


def _normalize_args(args: dict):
    return {k: args[k] for k in args if k in _keys}


class builder(object):
    '''
    Build packs.
    The builder accepts the building args, then build the packs on demand.
    '''

    def __init__(self, main_res_path: str, module_info: dict):
        self.__main_res_path = main_res_path
        self.__module_info = module_info
        self._logger = logger()
        self._digest = ''
        self.clean_status()

    @property
    def build_args(self):
        return self.__build_args

    @build_args.setter
    def build_args(self, value: dict):
        self.__build_args = _normalize_args(value)
        self._digest = sha256(json.dumps(
            self.__build_args).encode('utf8')).hexdigest()

    @property
    def warning_count(self):
        return self._warning_count

    @property
    def error_code(self):
        return self._error_code

    @property
    def file_name(self):
        return self._file_name

    @property
    def main_resource_path(self):
        return self.__main_res_path

    @property
    def module_info(self):
        return self.__module_info

    @property
    def build_log(self):
        return self._logger.raw_log

    def clean_status(self):
        self._warning_count = 0
        self._error_code = ERR_OK
        self._logger.clear()
        self._file_name = ""

    def _raise_warning(self, msg: dict):
        entry = f"Warning [{msg['code']}]: {msg['message']}"
        self._logger.append(entry)
        self._warning_count += 1

    def _raise_error(self, msg: dict):
        entry = f"Error [{msg['code']}]: {msg['message']}"
        terminate_msg = "Terminate building because an error occurred."
        self._logger.append(entry)
        self._logger.append(terminate_msg)
        self._error_code = msg['code']

    def _get_lists(self):
        # get language modules
        lang_supp = self._parse_includes("language")
        # get resource modules
        res_supp = self._parse_includes("resource")
        # get mixed modules
        mixed_supp = self._parse_includes("mixed")
        # get module collections
        module_collection = self._parse_includes("collection")
        # add modules to respective list
        self._handle_modules(res_supp, lang_supp,
                             mixed_supp, module_collection)
        return lang_supp, res_supp

    def _create_dir(self):
        # mkdir
        if os.path.exists(self.__build_args['output']) and not os.path.isdir(self.__build_args['output']):
            os.remove(self.__build_args['output'])
        if not os.path.exists(self.__build_args['output']):
            os.mkdir(self.__build_args['output'])
        return os.path.join(self.__build_args['output'], self._file_name)

    def _parse_includes(self, type: str) -> list:
        includes = self.build_args['modules'][type]
        full_list = list(
            map(lambda item: item['name'], self.module_info['modules'][type]))
        if 'none' in includes:
            return []
        elif 'all' in includes:
            return full_list
        else:
            include_list = []
            for item in includes:
                if item in full_list:
                    include_list.append(item)
                else:
                    self._raise_warning(_build_message(
                        WARN_MODULE_NOT_FOUND, f'Module "{item}" does not exist, skipping.'))
            return include_list

    def _handle_modules(self, resource_list: list, language_list: list, mixed_list: list, collection_list: list):
        # get all resource, language and mixed modules supplied by collection
        collection_info = {
            k.pop('name'): k for k in self.module_info['modules']['collection']}
        for collection in collection_list:
            for module_type, module_list in (('language', language_list), ('resource', resource_list), ('mixed', mixed_list)):
                if module_type in collection_info[collection]['contains']:
                    module_list.extend(
                        collection_info[collection]['contains'][module_type])
        # mixed_modules go to resource and language, respectively
        resource_list.extend(mixed_list)
        language_list.extend(mixed_list)

    def _merge_language(self, main_lang_data: dict, lang_supp: list):
        lang_data = main_lang_data
        module_path = self.module_info['path']
        for item in lang_supp:
            add_file = os.path.join(module_path, item, "add.json")
            remove_file = os.path.join(module_path, item, "remove.json")
            if os.path.exists(add_file):
                lang_data |= json.load(open(add_file, 'r', encoding='utf8'))
            if os.path.exists(remove_file):
                for key in json.load(open(remove_file, 'r', encoding='utf8')):
                    if key in lang_data:
                        lang_data.pop(key)
                    else:
                        self._raise_warning(_build_message(
                            WARN_KEY_NOT_FOUND, f'Key "{key}" does not exist, skipping.'))
        return lang_data
