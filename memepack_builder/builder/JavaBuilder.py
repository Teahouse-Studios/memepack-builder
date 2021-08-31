import json
import os
from .base import PackBuilder
from ..utils import generate_java_legacy, generate_json


class JavaBuilder(PackBuilder):
    def __init__(self, main_res_path: str, module_overview: dict, mod_path: str, options: dict = None):
        super().__init__(main_res_path, module_overview, options)
        self.mod_path = os.path.abspath(mod_path)

    def validate_options(self):
        latest_je = self._config['latestJEPackFormat']
        legacy_je = self._config['legacyJEPackFormat']
        je_required = ['type', 'modules', 'mod', 'output', 'hash']
        options = self.options
        for option in je_required:
            if option not in options:
                self._append_log(
                    f'Warning: Missing required argument "{option}".')
                return False
        # validate 'format' option
        if 'format' not in options:
            options['format'] = options['type'] == 'legacy' and legacy_je or latest_je
            self._append_log(
                f'Warning: Did not specify "pack_format". Assuming value is "{options["format"]}".')
        else:
            if (options['type'] == 'legacy' and options['format'] != legacy_je) or \
                    (options['type'] in ['normal', 'compat'] and options['format'] <= legacy_je):
                self._append_log(
                    f'Error: Type "{options["type"]}" does not match pack_format {options["format"]}.')
                return False
        return True

    def build(self):
        if not self.validate_options():
            return
        self._normalize_options()
        self._merge_collection_into_resource()
        extra_files = ['LICENSE', 'pack.png']
        extra_content = {}
        self._add_language(extra_files, extra_content)
        self._build(extra_files, extra_content)

    def get_language_content(self, lang_file_path: str, with_modules: bool):
        def lang_module_filter(name):
            for v in self.module_overview['modules']['resource']:
                if v['name'] == name and 'modified_language' in v['classifier']:
                    return True
            return False
        options = self.options
        lang_modules = list(
            filter(lang_module_filter, options['modules']['resource']))
        if options['type'] in ('normal', 'compat'):
            result = generate_json(
                lang_file_path, with_modules, self.module_overview, lang_modules, options['mod'])
            self._append_log(*result['log'])
            return result['content']
        elif options['type'] == 'legacy':
            result = generate_java_legacy(
                lang_file_path, with_modules, self.module_overview, lang_modules, options['mod'])
            self._append_log(*result['log'])
            return result['content']
        else:
            return ''

    def _normalize_options(self):
        options = self.options
        if options['mod']:
            options['mod'] = list(map(lambda v: os.path.abspath(
                os.path.join(self.mod_path, v)), options['mod']))
        options['outputName'] = os.path.abspath(os.path.join(
            options["outputDir"], f'{options["outputName"] or self._config["defaultFileName"]}.zip'))

    def _add_language(self, file_list: list[str], content_list: dict):
        if self.options['type'] == 'normal':
            file_list.append('pack.mcmeta')
            content_list['assets/minecraft/lang/zh_meme.json'] = self.get_language_content(
                f'{self.main_resource_path}/assets/minecraft/lang/zh_meme.json', True)
            content_list['assets/realms/lang/zh_meme.json'] = self.get_language_content(
                f'{self.main_resource_path}/assets/realms/lang/zh_meme.json', False)
        elif self.options['type'] == 'compat':
            content_list['pack.mcmeta'] = json.dumps(
                self._process_mcmeta_file(), ensure_ascii=False, indent=4)
            content_list['assets/minecraft/lang/zh_cn.json'] = self.get_language_content(
                f'{self.main_resource_path}/assets/minecraft/lang/zh_meme.json', True)
            content_list['assets/realms/lang/zh_cn.json'] = self.get_language_content(
                f'{self.main_resource_path}/assets/realms/lang/zh_meme.json', False)
        elif self.options['type'] == 'legacy':
            content_list['pack.mcmeta'] = json.dumps(
                self._process_mcmeta_file(), ensure_ascii=False, indent=4)
            content_list['assets/minecraft/lang/zh_cn.lang'] = self.get_language_content(
                f'{self.main_resource_path}/assets/minecraft/lang/zh_meme.json', True)
            content_list['assets/realms/lang/zh_cn.lang'] = self.get_language_content(
                f'{self.main_resource_path}/assets/realms/lang/zh_meme.json', False)

    def _process_mcmeta_file(self):
        loaded_data = json.load(
            open(f'{self.main_resource_path}/pack.mcmeta', encoding='utf8'))
        if self.options['type'] == 'compat':
            del loaded_data['language']
        pack_format = self.options['type'] and self._config['legacyJEPackFormat'] or self.options['format']
        loaded_data['pack']['pack_format'] = pack_format or self._config['latestJEPackFormat']
        return loaded_data
