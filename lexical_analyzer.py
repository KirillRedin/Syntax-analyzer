from lexeme import Lexeme
from lexemes_table import LexemesTable
from error import Error
from tabulate import tabulate


class LexicalAnalyzer:
    def __init__(self):
        self.keywordsTable = {'PROGRAM': 401,
                              'BEGIN': 402,
                              'END': 403,
                              'VAR': 404,
                              'INTEGER': 405,
                              'FLOAT': 406,
                              'IF': 407,
                              'THEN': 408,
                              'ELSE': 409,
                              'ENDIF': 410}

        self.symbolCategories = {0: 'WHITESPACE',
                                 1: 'DIGIT',
                                 2: 'LETTER',
                                 3: 'DELIMITER',
                                 4: 'COMMENT',
                                 5: 'ERROR'}

        self.lexemeCategories = ['KEYWORD',
                                 'U_INT',
                                 'IDENTIFICATOR',
                                 'DELIMITER']

        self.uIntsTable = LexemesTable(501)
        self.idnTable = LexemesTable(1001)
        self.delTable = {}
        self.lexemesTable = []
        self.errors = []
        self.line_number = self.column_number = 0
        self.buf = ''
        self.is_comment = False
        self.fill_del_table()

    def parse(self, name):

        file = open(name, "r")
        comment_line = comment_col = 0

        for line in file:
            self.line_number += 1
            self.column_number = 0

            for character in line:
                self.column_number += 1

                if self.is_comment:
                    if character == ')':
                        if line[self.column_number - 2] == '*'and (self.line_number != comment_line
                                                                   or comment_col != self.column_number - 2):
                            self.is_comment = False
                    continue

                elif self.get_category(character) == 'LETTER':
                    if self.buf.isdigit():
                        self.errors.append(Error("Unexpected symbol '%c'" % character, self.line_number,
                                                 self.column_number))
                        self.get_lexeme()
                    self.buf += character

                elif self.get_category(character) == 'DIGIT':
                    self.buf += character

                elif self.get_category(character) == 'DELIMITER':
                    if self.buf != '':
                        self.get_lexeme()
                        self.buf = character
                        self.get_lexeme()
                    self.buf = character
                    self.get_lexeme()

                elif self.get_category(character) == 'COMMENT':
                    if line[self.column_number] == '*':
                        self.is_comment = True
                        comment_line = self.line_number
                        comment_col = self.column_number
                    else:
                        self.errors.append(Error("Invalid token '(', '(*' expected",
                                                 self.line_number, self.column_number))
                    if self.buf != '':
                        self.get_lexeme()

                elif self.get_category(character) == 'WHITESPACE':
                    if self.buf != '':
                        self.get_lexeme()

                else:
                    self.errors.append(Error("Illegal character '%c' detected" % character,
                                             self.line_number, self.column_number))
                    if self.buf != '':
                        self.get_lexeme()

        if self.is_comment:
            self.errors.append(Error("End of file found, '*)' expected", comment_line, comment_col))
        else:
            if self.buf != '':
                self.get_lexeme()

    def get_category(self, character):

        if ord(character) == 32 or 8 <= ord(character) <= 14:
            return self.symbolCategories[0]

        elif 48 <= ord(character) <= 57:
            return self.symbolCategories[1]

        elif 65 <= ord(character) <= 90:
            return self.symbolCategories[2]

        elif ord(character) == 46 or ord(character) == 58 or ord(character) == 59 or ord(character) == 61:
            return self.symbolCategories[3]

        elif ord(character) == 40:
            return self.symbolCategories[4]

        else:
            return self.symbolCategories[5]

    def get_lexeme(self):

        if self.buf in self.keywordsTable:
            keyword_lexeme = Lexeme(self.buf, self.keywordsTable[self.buf], self.line_number,
                                    self.column_number - len(self.buf))
            self.lexemesTable.append(keyword_lexeme)

        elif self.buf in self.delTable:
            delim_lexeme = Lexeme(self.buf, self.delTable[self.buf], self.line_number,
                                  self.column_number - len(self.buf) + 1)
            self.lexemesTable.append(delim_lexeme)

        elif self.buf.isdigit():
            u_int_lexeme = self.uIntsTable.add(int(self.buf), self.line_number, self.column_number - len(self.buf))
            self.lexemesTable.append(u_int_lexeme)
            
        else:
            idn_lexeme = self.idnTable.add(self.buf, self.line_number, self.column_number - len(self.buf))
            self.lexemesTable.append(idn_lexeme)

        self.buf = ''

    def fill_del_table(self):

        delimiters = ['.', '=', ':', ';']

        for delimiter in delimiters:
            self.delTable[delimiter] = ord(delimiter)

    def print_result(self):

        headers = ['LEXEME', 'TOKEN', 'CODE', 'LINE_NUM', 'COL_NUM']
        lexemes_table = []

        for lexeme in self.lexemesTable:
            lexemes_table.append([lexeme.value, lexeme.code, lexeme.line_num, lexeme.col_num])

        print(tabulate(lexemes_table, headers))
        print()

        for error in self.errors:
            print('Error (line %d col %d):' % (error.line_num, error.col_num), error.text)


analyzer = LexicalAnalyzer()
analyzer.parse('true1')
analyzer.print_result()
