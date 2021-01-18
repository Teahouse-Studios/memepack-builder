from .err_code import *

def _build_message(code: int, message: str):
    return {'code': code, 'message': message}