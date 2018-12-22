import sys
import os


class JackTokenizer:
    """
    Removes all comments adn white space from the input stream and breaks it into
    Jack-language tokens, as specified by the Jack grammer
    """
    # token_type
    KEYWORD = "keyword"
    SYMBOL = "symbol"
    IDENTIFIER = "identifier"
    INT_CONSTANT = "integerConstant"
    STRING_CONSTANT = "stringConstant"
    # keyWord
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    INT = "int"
    BOOLEAN = "boolean"
    CHAR = "char"
    VOID = "void"
    VAR = "var"
    STATIC = "static"
    FIELD = "field"
    LET = "let"
    DO = "do"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    THIS = "this"
    keywords = [CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT, BOOLEAN, CHAR, VOID, VAR, STATIC, FIELD, LET,
                DO, IF, ELSE, WHILE, RETURN, TRUE, FALSE, NULL, THIS]
    # symbols
    OPEN_CURLY = '{'
    CLOSE_CURLY = '}'
    OPEN_BRACK = '('
    CLOSE_BRACK = ')'
    OPEN_SQUARE = '['
    CLOSE_SQUARE = ']'
    DOT = '.'
    COMMA = ','
    SEMICOLON = ';'
    PLUS = '+'
    MINUS = '-'
    STAR = '*'
    DIVIDE = '/'
    AND = '&'
    OR = '|'
    LESS = '<'
    GREATER = '>'
    EQUAL = '='
    NOT_EQUAL = '~'
    symbols = [OPEN_CURLY, CLOSE_CURLY, OPEN_BRACK, CLOSE_BRACK, OPEN_SQUARE, CLOSE_SQUARE, DOT, COMMA, SEMICOLON, PLUS,
               MINUS, STAR, DIVIDE, AND, OR, LESS, GREATER, EQUAL, NOT_EQUAL]

    def __init__(self, file_name):
        """
        Opens the input file/stream and gets ready to tokenize it
        """
        self._file_name = file_name
        self._file = None
        self._current_word = 0
        with open(file_name, 'r') as f:
            self._file = f.read()
        # remove single line comments of type // until end of line
        self._remove_comments('//', '\n')
        # remove multi line comments
        self._remove_comments('/*', '*/', True)
        indices = self._find_string()
        words = self._split(indices)
        self._stack = Stack()
        self._stack.convert_list_stack(words)

    def _split(self, indices):
        words = []
        start_index = 0
        for (s, e) in indices:
            words += self._file[start_index:s].split()
            words.append(self._file[s:e + 1])
            start_index = e + 1
        words += self._file[start_index:].split()
        return words

    def has_more_tokens(self):
        """
        Do we have more tokens in the input

        :return:
        Returns true if there are more tokens, false otherwise
        """
        return not self._stack.is_empty()

    def advance(self):
        """
        Gets the next token from the input and makes it the current token.
        This method should only be called if has_more_tokens() is true.
        Initially there is no current token
        :return:
        Returns next token from input
        """
        self._stack.pop()

    def token_type(self):
        """
        :return:
        Returns the type of the current token
        """
        set_token_type = None
        while not set_token_type:
            item = self._stack.peek()
            if item in JackTokenizer.keywords:
                set_token_type = JackTokenizer.KEYWORD
            elif item.isdigit():
                set_token_type = JackTokenizer.INT_CONSTANT
            elif item.startswith('"') and item.endswith('"'):
                set_token_type = JackTokenizer.STRING_CONSTANT
            elif item.startswith('"'):
                raise Exception("No closing string quotations")
            elif item in JackTokenizer.symbols:
                set_token_type = JackTokenizer.SYMBOL
            elif self._split_symbol(item):
                set_token_type = None
            else:
                set_token_type = JackTokenizer.IDENTIFIER
        return set_token_type

    def _split_symbol(self, item):
        for symbol in JackTokenizer.symbols:
            if symbol in item:
                index = item.find(symbol)
                if index == 0:
                    word1 = item[0]
                    word2 = item[1:]
                elif index == len(item) - 1:
                    word1 = item[0:len(item) - 1]
                    word2 = item[-1]
                else:
                    word1 = item[0:index]
                    word2 = item[index:]
                self.advance()
                self._stack.push(word2)
                self._stack.push(word1)
                return True
        return False

    def keyword(self):
        """

        :return:
        Returns the keyword which is the current token .
        Should be called only when token_type() is KEYWORD
        """
        for keyword in JackTokenizer.keywords:
            if self._stack.peek() == keyword:
                return keyword

    def symbol(self):
        """

        :return:
        Returns the keyword which is the current token .
        Should be called only when token_type() is SYMBOL
        """
        for symbol in JackTokenizer.symbols:
            if self._stack.peek() == symbol:
                if symbol == JackTokenizer.LESS:
                    return "&lt;"
                if symbol == JackTokenizer.GREATER:
                    return "&gt;"
                if symbol == JackTokenizer.AND:
                    return "&amp;"
                return symbol

    def identifier(self):
        """

        :return:
        Returns the identifier which is the current token .
        Should be called only when token_type() is IDENTIFIER
        """
        return self._stack.peek()

    def int_val(self):
        """

        :return:
        Returns the integer which is the current token .
        Should be called only when token_type() is INT_CONST
        """
        return self._stack.peek()

    def string_val(self):
        """

        :return:
        Returns the string value which is the current token without the double quotes .
        Should be called only when token_type() is STRING_CONST
        """
        return self._stack.peek().strip('"')

    def value(self):
        map = {JackTokenizer.KEYWORD: self.keyword,
               JackTokenizer.SYMBOL: self.symbol,
               JackTokenizer.IDENTIFIER: self.identifier,
               JackTokenizer.STRING_CONSTANT: self.string_val,
               JackTokenizer.INT_CONSTANT: self.int_val}
        return map[self.token_type()]()

    def _remove_comments(self, start_pat, end_pat, is_multiline=False):
        """
        Remove comments from source code using start and end pat
        :return:
        """
        index1 = self._file.find(start_pat)
        if index1 == -1:  # check if pattern in source file
            return
        index2 = self._file.find(end_pat, index1 + 1)
        if index2 == -1:  # remove rest of file (since commented)
            self._file = self._file[0:index1]
            return
        while index1 != -1:
            if is_multiline:
                index2 = index2 + 1
            self._file = self._file[0:index1] + self._file[index2 + 1:]
            index1 = self._file.find(start_pat)
            index2 = self._file.find(end_pat, index1 + 1)
            if index2 == -1:
                self._file = self._file[0:index1]
                index1 = -1

    def _find_string(self):
        """
        Remove comments from source code using start and end pat
        :return:
        """
        indices = []
        index1 = self._file.find('"')
        if index1 == -1:  # check if pattern in source file
            return indices
        index2 = self._file.find('"', index1 + 1)
        if index2 == -1:  # remove rest of file (since commented)
            raise Exception("No closing string quote")
        while index1 != -1:
            indices.append((index1, index2))
            index1 = self._file.find('"', index2 + 1)
            index2 = self._file.find('"', index1 + 1)
            if index2 == -1:
                index1 = -1
        return indices


class JackAnalyzer:
    """
    top level driver that sets up and invokes the other modules

    """
    TOKENIZER_FILE = "T.xml"
    ANALYZER_FILE = ".xml"
    JACK_FILE = ".jack"

    """
    Static method to run the program
    """
    @staticmethod
    def run(path):
        jack_file = path.split("/")[-1]
        tokenizer_file = jack_file[0:jack_file.find(".")] + JackAnalyzer.TOKENIZER_FILE
        analyzer_file = jack_file[0:jack_file.find(".")] + JackAnalyzer.ANALYZER_FILE
        tokenizer_file = os.path.join(os.path.dirname(path), tokenizer_file)
        analyzer_file = os.path.join(os.path.dirname(path), analyzer_file)
        tokenizer = JackTokenizer(path)
        JackAnalyzer.construct_xml(tokenizer_file, tokenizer)
        tokenizer = JackTokenizer(path)
        CompilationEngine(tokenizer, analyzer_file)

    """
    Static method to run program depending of file/dir passed as argument
    """
    @staticmethod
    def check_dir():
        path = str(sys.argv[1])
        if os.path.isfile(path):
            if path.endswith(JackAnalyzer.JACK_FILE):
                JackAnalyzer.run(path)
            else:
                raise Exception("Filename should end with .jack")
        elif os.path.isdir(path):
            for filename in os.listdir(path):
                if filename.endswith(JackAnalyzer.JACK_FILE):
                    file = os.path.join(path, filename)
                    JackAnalyzer.run(file)
        else:
            raise Exception("Not a valid file/path")

    @staticmethod
    def construct_xml(file_name, tokenizer):
        file = open(file_name, "w")
        file.write('<tokens>')
        file.write('\n')
        while tokenizer.has_more_tokens():
            file.write('<{t}>'.format(t=tokenizer.token_type()))
            file.write(tokenizer.value())
            file.write('</{t}>'.format(t=tokenizer.token_type()))
            file.write('\n')
            tokenizer.advance()
        file.write('</tokens>')


class Stack:
        """
        Class which encapsulates push/pop operations
        Used by Jack tokenizer
        """

        def __init__(self):
            self._first = None

        def push(self, item):
            temp = self._first
            self._first = Stack.Node(item)
            self._first.next = temp

        def pop(self):
            if self.is_empty():
                raise Exception("Cannot pop from empty stack")
            item = self._first.item
            self._first = self._first.next
            return item

        def peek(self):
            if self.is_empty():
                raise Exception("Cannot peek empty stack")
            return self._first.item

        def is_empty(self):
            return self._first is None

        def convert_list_stack(self, lst):
            for i in range(len(lst) - 1, -1, -1):
                item = lst[i]
                self.push(item)
            return self

        class Node:
            def __init__(self, item):
                self.item = item
                self.next = None


class CompilationEngine:
    """
    Effects the actual compliation output. Gets its input from a JackTokenizer and emits the parsed structure into an
    output file/stream. The output is generated by a series of compilexxx() routines, one for every syntactic element xxx
    of the Jack grammaer
    """

    def __init__(self, tokenizer, output):
        """
        Creates a new compilation engine with the given input and output
        :param tokenizer:
        :param output:
        """
        self._tokenizer = tokenizer
        self._output = open(output, "w")
        self._compile_grammar(self.compile_class)

    def _compile_grammar(self, function_name):
        self._print_tags(function_name, opening=True)
        #invoking function
        function_name()
        self._print_tags(function_name, opening=False)

    def _print_tags(self, function_name, opening):
        """
        Local helper function to print tags related to the different compiler elements
        :param function_name:
        :param opening:
        :return:
        """
        tags_map = {
                    self.compile_class: 'class',
                    self.compile_class_vardec: 'classVarDec',
                    self.compile_term: 'term',
                    self.compile_expression: 'expression',
                    self.compile_expressionlist: 'expressionList',
                    self.compile_vardec: 'varDec',
                    self.compile_statements: 'statements',
                    self.compile_if: 'ifStatement',
                    self.compile_let: 'letStatement',
                    self.compile_do: 'doStatement',
                    self.compile_return: 'returnStatement',
                    self.compile_while: 'whileStatement',
                    self.compile_subroutine: 'subroutineDec',
                    self.compile_subroutine_body: 'subroutineBody',
                    self.compile_parameterlist: 'parameterList',
                 }
        if opening:
            self._output.write('<{tag}>'.format(tag=tags_map[function_name]))
        else:
            self._output.write('</{tag}>'.format(tag=tags_map[function_name]))
        self._output.write('\n')

    def compile_class(self):
        """
        Compiles a complete class
        Grammar: 'class' className '{' classVarDec* subroutineDec* '}'
        :return:
        """
        self._eat(JackTokenizer.CLASS)
        self._eat(None)
        self._eat(JackTokenizer.OPEN_CURLY)
        self._class_var_dec_opt()
        self._subroutine_dec_opt()
        self._eat(JackTokenizer.CLOSE_CURLY)

    def _class_var_dec_opt(self):
        """
        Local recursive helper for the following optional
        GRAMMAR classVarDec*
        :return:
        """
        class_var_dec_str = [JackTokenizer.STATIC, JackTokenizer.FIELD]
        if self._tokenizer.has_more_tokens and self._tokenizer.value() in class_var_dec_str:
            self._compile_grammar(self.compile_class_vardec)
            self._class_var_dec_opt()

    def _subroutine_dec_opt(self):
        """
        Local recursive helper for the following optional
        GRAMMAR subroutineDec*
        :return:
        """
        subroutine_dec_str = [JackTokenizer.CONSTRUCTOR, JackTokenizer.FUNCTION, JackTokenizer.METHOD]
        if self._tokenizer.has_more_tokens and self._tokenizer.value() in subroutine_dec_str:
            self._compile_grammar(self.compile_subroutine)
            self._subroutine_dec_opt()
        else:
            return

    def compile_class_vardec(self):
        """
        Compiles a static declaration or a field declaration
        Grammar: ('static' | 'field') type varName (',' varName)* ';'
        :return:
        """
        # refers to static/field
        self._eat(self._tokenizer.value())
        types = [JackTokenizer.INT, JackTokenizer.CHAR, JackTokenizer.BOOLEAN]
        if self._tokenizer.has_more_tokens and self._tokenizer.value() in types:
            self._eat(self._tokenizer.value())
        else:
            # identifier for className
            self._eat(None)
        # identifier for varName
        self._eat(None)
        self._var_name_opt()
        self._eat(JackTokenizer.SEMICOLON)

    def _var_name_opt(self):
        """
        Local recursive helper for the following optional
        GRAMMAR (',' varName)*
        :return:
        """
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.COMMA:
            self._eat(JackTokenizer.COMMA)
            # identifer for varName
            self._eat(None)
            self._var_name_opt()

    def compile_subroutine(self):
        """
        Compiles a complete method, function or constructor
        Grammar: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        :return:
        """
        # refers to constructor/function/method
        self._eat(self._tokenizer.value())
        ret_types = [JackTokenizer.INT, JackTokenizer.CHAR, JackTokenizer.BOOLEAN, JackTokenizer.VOID]
        if self._tokenizer.value() in ret_types:
            self._eat(self._tokenizer.value())
        else:
            # identifer for className
            self._eat(None)
        # identifier for subroutineName
        self._eat(None)
        self._eat(JackTokenizer.OPEN_BRACK)
        self._compile_grammar(self.compile_parameterlist)
        self._eat(JackTokenizer.CLOSE_BRACK)
        self._compile_grammar(self.compile_subroutine_body)

    def compile_subroutine_body(self):
        """
        Compiles the subroutine body
        Grammar: '{' varDec* statements '}'
        :return:
        """
        self._eat(JackTokenizer.OPEN_CURLY)
        self._var_dec_opt()
        self._compile_grammar(self.compile_statements)
        self._eat(JackTokenizer.CLOSE_CURLY)

    def _var_dec_opt(self):
        """
        Local recursive helper for the following optional
        GRAMMAR (varDec)*
        :return:
        """
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.VAR:
            self._compile_grammar(self.compile_vardec)
            self._var_dec_opt()

    def _var_opt(self):
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.COMMA:
            self._eat(JackTokenizer.COMMA)
            self._eat(None)
            self._var_opt()
        else:
            return

    def _type_var_name_opt(self):
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.COMMA:
            self._eat(JackTokenizer.COMMA)
            if not self._compile_params():
                raise Exception("Token mismatch for paramList")
            self._type_var_name_opt()
        else:
            return

    def compile_parameterlist(self):
        """
        Compiles a (possibly empty parameter list, not including the enclosing "()"
        Grammaer: ((type varName) (',' type varName)*)?
        :return:
        """
        self._compile_params()
        self._type_var_name_opt()

    def _compile_params(self):
        types = [JackTokenizer.INT, JackTokenizer.CHAR, JackTokenizer.BOOLEAN]
        if self._tokenizer.has_more_tokens() and self._tokenizer.value() in types:
            self._eat(self._tokenizer.value())
            self._eat(None)
            return True
        elif self._tokenizer.has_more_tokens() and self._tokenizer.token_type() == JackTokenizer.IDENTIFIER:
            self._eat(None)
            self._eat(None)
            return True
        return False

    def compile_vardec(self):
        """
        Compiles a var declaration
        Grammar: 'var' type varName (',' varName)* ';'
        :return:
        """
        self._eat(JackTokenizer.VAR)
        types = [JackTokenizer.INT, JackTokenizer.CHAR, JackTokenizer.BOOLEAN]
        if self._tokenizer.value() in types:
            self._eat(self._tokenizer.value())
        else:
            # identifer for className
            self._eat(None)
        # identifier for varName
        self._eat(None)
        self._var_opt()
        self._eat(JackTokenizer.SEMICOLON)

    def compile_statements(self):
        """
        Compiles a sequence of statements, not including the enclosing "{}"
        Grammar: letStatement | ifStatement | whileStatement | doStatement | returnStatement
        :return:
        """
        keyword_function_map = {
                            JackTokenizer.LET: self.compile_let,
                            JackTokenizer.IF : self.compile_if,
                            JackTokenizer.WHILE: self.compile_while,
                            JackTokenizer.DO: self.compile_do,
                            JackTokenizer.RETURN: self.compile_return
                            }
        if self._tokenizer.has_more_tokens and self._tokenizer.value() in keyword_function_map:
            self._compile_grammar(keyword_function_map[self._tokenizer.value()])
            self.compile_statements()

    def compile_do(self):
        """
        Compiles a do statement
        Grammar: 'do' subroutineCall ';'
        :return:
        """
        self._eat(JackTokenizer.DO)
        self._eat(None)
        # dealing with subroutineCall
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.OPEN_BRACK:
            self._eat(JackTokenizer.OPEN_BRACK)
            self._compile_grammar(self.compile_expressionlist)
            self._eat(JackTokenizer.CLOSE_BRACK)
        elif self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.DOT:
            self._eat(JackTokenizer.DOT)
            self._eat(None)
            self._eat(JackTokenizer.OPEN_BRACK)
            self._compile_grammar(self.compile_expressionlist)
            self._eat(JackTokenizer.CLOSE_BRACK)
        #### end of subroutineCall
        self._eat(JackTokenizer.SEMICOLON)

    def compile_let(self):
        """
        Compiles a let statement
        Grammar: 'let' varName ('[' expression ']')? '=' expression ';'
        :return:
        """
        self._eat(JackTokenizer.LET)
        self._eat(None)
        ######## optional ############
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.OPEN_SQUARE:
            self._eat(JackTokenizer.OPEN_SQUARE)
            self._compile_grammar(self.compile_expression)
            self._eat(JackTokenizer.CLOSE_SQUARE)
        #############################
        self._eat(JackTokenizer.EQUAL)
        self._compile_grammar(self.compile_expression)
        self._eat(JackTokenizer.SEMICOLON)

    def compile_while(self):
        """
        Compiles a while statement using following grammar mentioned below
        Grammar: 'while' '(' expression ')' '{' statements '}'
        :return:
        """
        self._eat(JackTokenizer.WHILE)
        self._eat(JackTokenizer.OPEN_BRACK)
        self._compile_grammar(self.compile_expression)
        self._eat(JackTokenizer.CLOSE_BRACK)
        self._eat(JackTokenizer.OPEN_CURLY)
        self._compile_grammar(self.compile_statements)
        self._eat(JackTokenizer.CLOSE_CURLY)

    def compile_return(self):
        """
        Compiles a return statement
        Grammar: 'return' expression? ';'
        :return:
        """
        self._eat(JackTokenizer.RETURN)
        ######OPTONAL#####################
        if self._tokenizer.has_more_tokens and self._tokenizer.value() != JackTokenizer.SEMICOLON:
            self._compile_grammar(self.compile_expression)
        self._eat(JackTokenizer.SEMICOLON)

    def compile_if(self):
        """
        Compiles an if statement, possibly with a trailing else clause
        Grammar: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        :return:
        """
        self._eat(JackTokenizer.IF)
        self._eat(JackTokenizer.OPEN_BRACK)
        self._compile_grammar(self.compile_expression)
        self._eat(JackTokenizer.CLOSE_BRACK)
        self._eat(JackTokenizer.OPEN_CURLY)
        self._compile_grammar(self.compile_statements)
        self._eat(JackTokenizer.CLOSE_CURLY)
        ######## optional ############
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.ELSE:
            self._eat(JackTokenizer.ELSE)
            self._eat(JackTokenizer.OPEN_CURLY)
            self._compile_grammar(self.compile_statements)
            self._eat(JackTokenizer.CLOSE_CURLY)
        #############################

    def compile_expression(self):
        """
        Compiles an expression
        :return:
        Grammar: term (op term)*
        """
        self._compile_grammar(self.compile_term)
        self._ops_term_opt()

    def _ops_term_opt(self):
        ops = [JackTokenizer.PLUS, JackTokenizer.MINUS, JackTokenizer.STAR, JackTokenizer.DIVIDE, '&amp;',
               JackTokenizer.OR, '&lt;', '&gt;', JackTokenizer.EQUAL]
        if self._tokenizer.has_more_tokens and self._tokenizer.value() in ops:
            self._eat(self._tokenizer.value())
            self._compile_grammar(self.compile_term)
            self._ops_term_opt()

    def compile_term(self):
        """
        Compiles a term
        :return:
        Grammar: integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' |
                 subroutineCall  | unaryOp term
        """
        keyword_list = [JackTokenizer.TRUE, JackTokenizer.FALSE, JackTokenizer.NULL, JackTokenizer.THIS]
        unary_op = [JackTokenizer.MINUS, JackTokenizer.NOT_EQUAL]
        if self._tokenizer.has_more_tokens() and self._tokenizer.token_type() == JackTokenizer.INT_CONSTANT:
            self._eat(self._tokenizer.value())
        elif self._tokenizer.has_more_tokens() and self._tokenizer.token_type() == JackTokenizer.STRING_CONSTANT:
            self._eat(self._tokenizer.value())
        elif self._tokenizer.has_more_tokens() and self._tokenizer.value() in keyword_list:
            self._eat(self._tokenizer.value())
        elif self._tokenizer.has_more_tokens() and self._tokenizer.token_type() == JackTokenizer.IDENTIFIER:
            self._eat(None)
            if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.OPEN_SQUARE:
                self._eat(JackTokenizer.OPEN_SQUARE)
                self._compile_grammar(self.compile_expression)
                self._eat(JackTokenizer.CLOSE_SQUARE)
            #### dealing with subroutineCall
            elif self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.OPEN_BRACK:
                self._eat(JackTokenizer.OPEN_BRACK)
                self._compile_grammar(self.compile_expressionlist)
                self._eat(JackTokenizer.CLOSE_BRACK)
            elif self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.DOT:
                self._eat(JackTokenizer.DOT)
                self._eat(None)
                self._eat(JackTokenizer.OPEN_BRACK)
                self._compile_grammar(self.compile_expressionlist)
                self._eat(JackTokenizer.CLOSE_BRACK)
            #### end of subroutineCall
        elif self._tokenizer.has_more_tokens() and self._tokenizer.value() == JackTokenizer.OPEN_BRACK:
            self._eat(JackTokenizer.OPEN_BRACK)
            self._compile_grammar(self.compile_expression)
            self._eat(JackTokenizer.CLOSE_BRACK)
        elif self._tokenizer.has_more_tokens() and self._tokenizer.value() in unary_op:
            self._eat(self._tokenizer.value())
            self._compile_grammar(self.compile_term)

    def compile_expressionlist(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions
        :return:
        Grammar: (expression (',' expression)*)?
        """
        if self._tokenizer.has_more_tokens and self._tokenizer.value() != JackTokenizer.CLOSE_BRACK:
            self._compile_grammar(self.compile_expression)
            self._expression_opt()

    def _expression_opt(self):
        """
        Local recursive helper to check for expressions
        :return:
        """
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.COMMA:
            self._eat(JackTokenizer.COMMA)
            self._compile_grammar(self.compile_expression)
            self._expression_opt()

    def _eat(self, string):
        """
        Private method to handle all compiler elements
        :param string:
        :return:
        """
        if string is None:
            if self._tokenizer.token_type() != JackTokenizer.IDENTIFIER:
                raise Exception("Identifier expected")
        elif self._tokenizer.value() != string:
            raise Exception(
                "Actual Token value {t} does not match Expected value {s}".format(t=self._tokenizer.value()(),
                                                                                  s=string))
        self._output.write('<{t}>'.format(t=self._tokenizer.token_type()))
        self._output.write(self._tokenizer.value())
        self._output.write('</{t}>'.format(t=self._tokenizer.token_type()))
        self._output.write('\n')
        if self._tokenizer.has_more_tokens():
            self._tokenizer.advance()


if __name__ == '__main__':
    """
    Entry point of program for execution
    """
    JackAnalyzer.check_dir()
