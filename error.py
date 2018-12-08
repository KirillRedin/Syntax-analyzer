class Error:
    def __init__(self, text, line_num, col_num):
        self._text = text
        self._line_num = line_num
        self._col_num = col_num

    @property
    def text(self):
        return self._text

    @property
    def line_num(self):
        return self._line_num

    @property
    def col_num(self):
        return self._col_num
