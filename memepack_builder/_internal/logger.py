class logger(object):
    def __init__(self):
        self.__log = []

    @property
    def raw_log(self):
        return self.__log

    @property
    def log(self):
        return '\n'.join(self.__log)

    def append(self, line: str):
        self.__log.append(line)

    def clear(self):
        self.__log.clear()