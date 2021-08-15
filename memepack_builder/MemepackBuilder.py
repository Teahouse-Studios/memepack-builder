from .builder import JavaBuilder, BedrockBuilder
from .module_checker import ModuleChecker


class MemepackBuilder(object):
    def __init__(self, platform: str, resource_path: str, module_path: str, build_options: dict = None, mod_path: str = None) -> None:
        super().__init__()
        self.log = []
        self.module_checker = ModuleChecker(module_path)
        overview = self.module_checker.validate_modules()
        self.log.extend(self.module_checker.log)
        if platform == 'be':
            if build_options and build_options['type'] not in ('mcpack', 'zip'):
                raise ValueError('Platform does not match type.') from None
            self.builder = BedrockBuilder(
                resource_path, overview, build_options)
        elif platform == 'je':
            if build_options and build_options['type'] not in ('normal', 'compat', 'legacy'):
                raise ValueError('Platform does not match type.') from None
            mod_path = mod_path or ''
            self.builder = JavaBuilder(
                resource_path, overview, mod_path, build_options)
        else:
            raise ValueError('Unknown platform.') from None

    def build(self, clear_log: bool = True):
        if clear_log:
            self.log.clear()
        self.builder.build()
        self.log.extend(self.builder.log)
