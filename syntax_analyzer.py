from node import Node
from error import Error


class SyntaxAnalyzer:
    def __init__(self, lexemes_table):
        self.lexemesTable = lexemes_table
        self.errors = []
        self.lexeme_num = 0
        self.tree = None

    def analyze(self):
        if self.is_eof():
            self.errors.append(Error('File is empty', 0, 0))
            return False
        self.tree = Node('<signal-program>', 0)
        self.signal_program(self.tree)

    def signal_program(self, node):
        result = self.program(node.add_child(Node('<program>', node.depth + 1)))

        if self.is_eof() and not result:
            self.errors.append(Error("Unexpected End Of File after '%s'" % self.get_current_lexeme().value,
                               self.get_current_lexeme().line_num, self.get_current_lexeme().col_num))

    def program(self, node):
        current_lexeme = self.lexemesTable[self.lexeme_num]

        if current_lexeme.value == 'PROGRAM':
            node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))
            if self.is_eof():
                return False

            if not self.procedure_identifier(node.add_child(Node('<procedure-identifier>', node.depth + 1))):
                return False

            if self.is_eof():
                return False
            current_lexeme = self.get_next_lexeme()

            if current_lexeme.value == ';':
                node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))

                if self.block(node.add_child(Node('<block>', node.depth + 1))):
                    if self.is_eof():
                        return False
                    current_lexeme = self.get_next_lexeme()

                    if current_lexeme.value == '.':
                        node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))
                        return True
                    else:
                        self.errors.append(Error("Unexpected lexeme '%s'. Delimiter '.' expected" % current_lexeme.value,
                                                 current_lexeme.line_num, current_lexeme.col_num))
                        return False
            else:
                self.errors.append(Error("Unexpected lexeme '%s'. Delimiter ';' expected" % current_lexeme.value,
                                         current_lexeme.line_num, current_lexeme.col_num))
                return False
        else:
            self.errors.append(Error("Unexpected lexeme '%s'. Keyword 'PROGRAM' expected" % current_lexeme.value,
                                     current_lexeme.line_num, current_lexeme.col_num))
            return False

    def block(self, node):
        if self.variable_declarations(node.add_child(Node('<variable-declarations>', node.depth + 1))):
            if self.is_eof():
                return
            current_lexeme = self.get_current_lexeme()

            if current_lexeme.value == 'BEGIN':
                node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))

                if self.statements_list(node.add_child(Node('<statements-list>', node.depth + 1))):
                    if self.is_eof():
                        return
                    current_lexeme = self.get_next_lexeme()

                    if current_lexeme.value == 'END':
                        node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))
                        return True
                    else:
                        self.errors.append(Error("Unexpected lexeme '%s'. Keyword 'END' expected" % current_lexeme.value,
                                                 current_lexeme.line_num, current_lexeme.col_num))
                        return False
                else:
                    return False
            else:
                self.errors.append(Error("Unexpected lexeme '%s'. Keyword 'BEGIN' expected" % current_lexeme.value,
                                         current_lexeme.line_num, current_lexeme.col_num))
                return False
        else:
            return False

    def variable_declarations(self, node):
        if self.is_eof():
            return
        current_lexeme = self.get_next_lexeme()

        if current_lexeme.value == 'VAR':
            node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))

            if self.declarations_list(node.add_child(Node('<declarations-list>', node.depth + 1))):
                return True
            else:
                self.errors.append(Error("At least one declaration after 'VAR' keyword expected",
                                         current_lexeme.line_num, current_lexeme.col_num))
                return False
        else:
            node.add_child(Node('<empty>', node.depth + 1))
            return True

    def declarations_list(self, node):
        declaration_node = Node('<declaration>', node.depth + 1)

        if self.declaration(declaration_node):
            node.add_child(declaration_node)
            self.declarations_list(node.add_child(Node('<declaration-list>', node.depth + 1)))
            return True
        else:
            node.add_child(Node('<empty>', node.depth + 1))
            return False

    def declaration(self, node):
        if self.variable_identifier(node.add_child(Node('<variable-identifier>', node.depth + 1))):
            if self.is_eof():
                return
            current_lexeme = self.get_next_lexeme()

            if current_lexeme.value == ':':
                node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))

                if self.attribute(node.add_child(Node('<attribute>', node.depth + 1))):
                    if self.is_eof():
                        return
                    current_lexeme = self.get_next_lexeme()

                    if current_lexeme.value == ';':
                        node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))
                        return True
                    else:
                        self.errors.append(Error("Unexpected lexeme '%s'. Delimiter ';' expected" % current_lexeme.value,
                                                 current_lexeme.line_num, current_lexeme.col_num))
                        return False
                else:
                    return False
            else:
                self.errors.append(Error("Unexpected lexeme '%s'. Delimiter ':' expected" % current_lexeme.value,
                                         current_lexeme.line_num, current_lexeme.col_num))
                return False
        else:
            if self.is_eof():
                return
            current_lexeme = self.get_current_lexeme()

            if current_lexeme.value != 'BEGIN':
                self.errors.append(Error("Unexpected lexeme '%s', Identifier expected" % current_lexeme.value,
                                         current_lexeme.line_num, current_lexeme.col_num))
            return False

    def attribute(self, node):
        if self.is_eof():
            return
        current_lexeme = self.get_next_lexeme()

        if current_lexeme.value == 'INTEGER' or current_lexeme.value == 'FLOAT':
            node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))
            return True
        else:
            self.errors.append(Error("Unexpected lexeme '%s'. Keyword 'INTEGER' or 'FLOAT' expected"
                                     % current_lexeme.value, current_lexeme.line_num, current_lexeme.col_num))
            return False

    def statements_list(self, node):
        statement_node = Node('<statement>', node.depth + 1)

        if self.statement(statement_node):
            node.add_child(statement_node)
            self.statements_list(node.add_child(Node('<statement-list>', node.depth + 1)))
            return True
        else:
            node.add_child(Node('<empty>', node.depth + 1))
            return False

    def statement(self, node):
        if self.condition_statement(node.add_child(Node('<condition-statement>', node.depth + 1))):
            if self.is_eof():
                return
            current_lexeme = self.get_next_lexeme()

            if current_lexeme.value == 'ENDIF':
                node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))

                if self.is_eof():
                    return
                current_lexeme = self.get_next_lexeme()

                if current_lexeme.value == ';':
                    node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))
                    return True
                else:
                    self.errors.append(Error("Unexpected lexeme '%s'. Delimiter ';' expected" % current_lexeme.value,
                                             current_lexeme.line_num, current_lexeme.col_num))
                    return False
            else:
                self.errors.append(Error("Unexpected lexeme '%s'. Keyword 'ENDIF' expected" % current_lexeme.value,
                                         current_lexeme.line_num, current_lexeme.col_num))
                return False
        else:
            return False

    def condition_statement(self, node):
        if self.incomplete_condition_statement(node.add_child(Node('<incomplete-condition-statement>', node.depth + 1))):
            return self.alternative_part(node.add_child(Node('<alternative-part>', node.depth + 1)))
        else:
            return False

    def incomplete_condition_statement(self, node):
        if self.is_eof():
            return
        current_lexeme = self.get_next_lexeme()

        if current_lexeme.value == 'IF':
            node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))

            if self.conditional_expression(node.add_child(Node('<conditional-expression>', node.depth + 1))):
                if self.is_eof():
                    return
                current_lexeme = self.get_next_lexeme()

                if current_lexeme.value == 'THEN':
                    node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))

                    self.statements_list(node.add_child(Node('<statement-list>', node.depth + 1)))

                    return True
                else:
                    self.errors.append(Error("Unexpected lexeme '%s' Keyword 'THEN' expected" % current_lexeme.value,
                                             current_lexeme.line_num, current_lexeme.col_num))
                    return False
            else:
                return False
        else:
            self.get_previous_lexeme()
            return False

    def alternative_part(self, node):
        if self.is_eof():
            return
        current_lexeme = self.get_next_lexeme()

        if current_lexeme.value == 'ELSE':
            node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))

            self.statements_list(node.add_child(Node('<statement-list>', node.depth + 1)))
            return True
        else:
            node.add_child(Node('<empty>', node.depth + 1))
            self.get_previous_lexeme()
            return True

    def conditional_expression(self, node):
        if self.expression(node.add_child(Node('<expression>', node.depth + 1))):
            if self.is_eof():
                return
            current_lexeme = self.get_next_lexeme()

            if current_lexeme.value == '=':
                node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))
                return self.expression(node.add_child(Node('<expression>', node.depth + 1)))
            else:
                self.errors.append(Error("Unexpected lexeme '%s'. Delimiter '=' expected" % current_lexeme.value,
                                   current_lexeme.line_num, current_lexeme.col_num))
                return False
        else:
            return False

    def expression(self, node):
        variable_node = Node('<variable-identifier-node>', node.depth + 1)

        if self.variable_identifier(variable_node):
            node.add_child(variable_node)
            return True
        elif 500 < self.get_current_lexeme().code < 600:
            node.add_child(Node(str(self.get_current_lexeme().code) + ' ' + str(self.get_current_lexeme().value),
                                node.depth + 1))
            return True
        else:
            self.errors.append(Error("Incorrect expression. Identifier or Unsigned integer expected",
                                     self.get_current_lexeme().line_num, self.get_current_lexeme().col_num))

    def variable_identifier(self, node):
        return self.identifier(node.add_child(Node('<identifier>', node.depth + 1)))

    def procedure_identifier(self, node):
        return self.identifier(node.add_child(Node('<identifier>', node.depth + 1)))

    def identifier(self, node):
        if self.is_eof():
            return
        current_lexeme = self.get_next_lexeme()

        if 1000 < current_lexeme.code < 1100:
            node.add_child(Node(str(current_lexeme.code) + ' ' + current_lexeme.value, node.depth + 1))
            return True
        else:
            return False

    def get_next_lexeme(self):
        self.lexeme_num += 1
        return self.lexemesTable[self.lexeme_num]

    def is_eof(self):
        try:
            self.lexemesTable[self.lexeme_num + 1]
        except IndexError:
            return True

    def get_previous_lexeme(self):
        self.lexeme_num -= 1
        return self.lexemesTable[self.lexeme_num]

    def get_current_lexeme(self):
        return self.lexemesTable[self.lexeme_num]

    def print_result(self):
        try:
            self.tree.print()
        except AttributeError:
            return

    def print_errors(self):
        for error in self.errors:
            print('Error (line %d col %d):' % (error.line_num, error.col_num), error.text)


