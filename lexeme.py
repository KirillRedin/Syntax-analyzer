class Lexeme:
    def __init__(self, value, code, line_num, col_num):
        self._value = value
        self._code = code
        self._line_num = line_num
        self._col_num = col_num

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        self._code = code

    @property
    def line_num(self):
        return self._line_num

    @property
    def col_num(self):
        return self._col_num
