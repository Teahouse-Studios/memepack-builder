from .base import PackBuilder
from ..utils.LanguageGenerator import generate_java_legacy, generate_json


class JavaBuilder(PackBuilder):
    def __init__(self, main_res_path: str, module_overview: dict, mod_path: str, options: dict):
        super().__init__(main_res_path, module_overview, options)
        self.mod_path = mod_path

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
    
    def get_language_content(self):
        pass

    def _normalize_options(self):
        pass

    def _add_language(self):
        pass

    def _process_mcmeta_file(self):
        pass
