import json
import os
from .base import PackBuilder
from ..utils import generate_bedrock


class BedrockBuilder(PackBuilder):
    def __init__(self, main_res_path: str, module_overview: dict, options: dict = None):
        super().__init__(main_res_path, module_overview, options)

    def validate_options(self):
        be_required = ['type', 'compatible', 'modules', 'output', 'hash']
        options = self.options
        for option in be_required:
            if option not in options:
                self._append_log(
                    f'Warning: Missing required argument "{option}".')
                return False
        return True

    def build(self):
        if not self.validate_options():
            return
        self._normalize_options()
        self._merge_collection_into_resource()
        extra_files = ['pack_icon.png', 'manifest.json']
        extra_content = {
            'textures/item_texture.json': self.get_texture('item_texture.json'),
            'textures/terrain_texture.json': self.get_texture('terrain_texture.json')
        }
        self._add_language(extra_files, extra_content)
        self._build(extra_files, extra_content, [
                    'item_texture.json', 'terrain_texture.json'])

    def get_texture(self, file_name: str):
        texture = {'texture_data': {}}
        for module in self.options['modules']['resource']:
            path = f'{self.module_overview["modulePath"]}/{module}/textures/{file_name}'
            if os.path.exists(path):
                texture['texture_data'] |= json.load(
                    open(path, encoding='utf8'))['texture_data']
        if texture['texture_data'] == {}:
            return ''
        else:
            return json.dumps(texture, ensure_ascii=False, indent=4)

    def get_language_content(self, lang_file_path: str, with_modules: bool):
        result = generate_bedrock(f'{self.main_resource_path}/{lang_file_path}',
                                  with_modules, self.module_overview, self.options['modules']['resource'])
        self._append_log(*result['log'])
        return result['content']

    def _normalize_options(self):
        options = self.options
        options['outputName'] = os.path.abspath(os.path.join(
            options["outputDir"], f'{options["outputName"] or self._config["defaultFileName"]}.{options["type"]}'))

    def _add_language(self, file_list: list[str], content_list: dict):
        lang_content = self.get_language_content('texts/zh_ME.lang', True)
        if (self.options['compatible']):
            content_list['texts/zh_CN.lang'] = lang_content
        else:
            file_list.extend(('texts/language_names.json',
                             'texts/languages.json', 'texts/zh_CN.lang'))
            content_list['texts/zh_ME.lang'] = lang_content
