from lexeme import Lexeme


class LexemesTable:
    def __init__(self, code):
        self._lexemes = []
        self._code = code

    @property
    def get_table(self):
        return self._lexemes

    def add(self, value, line_number, column_number):
        if not self.get_by_value(value):
            lexeme = Lexeme(value, self._code, line_number, column_number)
            self._lexemes.append(lexeme)
            self._code += 1
            return lexeme
        return self.get_by_value(value)

    def get_by_value(self, value):
        for lexeme in self._lexemes:
            if lexeme.value == value:
                return lexeme
