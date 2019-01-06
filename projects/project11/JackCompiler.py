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
    # differentiate from MINUS
    UNARY_MINUS = '--'
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
                if index1 != -1:
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


class JackCompiler:
    """
    top level driver that sets up and invokes the other modules

    """
    VM_FILE = ".vm"
    JACK_FILE = ".jack"

    """
    Static method to run the program
    """

    @staticmethod
    def run(path):
        jack_file = path.split("/")[-1]
        vm_file = jack_file[0:jack_file.find(".")] + JackCompiler.VM_FILE
        vm_file = os.path.join(os.path.dirname(path), vm_file)
        tokenizer = JackTokenizer(path)
        CompilationEngine(tokenizer, vm_file)

    """
    Static method to run program depending of file/dir passed as argument
    """

    @staticmethod
    def check_dir():
        path = str(sys.argv[1])
        if os.path.isfile(path):
            if path.endswith(JackCompiler.JACK_FILE):
                JackCompiler.run(path)
            else:
                raise Exception("Filename should end with .jack")
        elif os.path.isdir(path):
            for filename in os.listdir(path):
                if filename.endswith(JackCompiler.JACK_FILE):
                    file = os.path.join(path, filename)
                    JackCompiler.run(file)
        else:
            raise Exception("Not a valid file/path")


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

    def __init__(self, tokenizer, output_file):
        """
        Creates a new compilation engine with the given input and output
        :param tokenizer:
        :param symbol_table:
        :param vmwriter:
        :param output:
        """
        self._tokenizer = tokenizer
        self._symbol_table = SymbolTable()
        self._vmwriter = VMWriter(output_file)
        # field variables required for code generation
        self._class_name = None
        self._function_name = None
        self._is_method = False
        self._is_void_function = False
        self._is_constructor = False
        self._no_arguments = 0
        self._ops_stack = Stack()
        # for generating unique if label
        self._ifid = -1
        # for generating unique while label
        self._whileid = -1
        self.compile_class()
        self._vmwriter.close()

    def _get_ifid(self):
        self._ifid = self._ifid + 1
        return str(self._ifid)

    def _get_whileid(self):
        self._whileid = self._whileid + 1
        return str(self._whileid)

    def compile_class(self):
        """
        Compiles a complete class
        Grammar: 'class' className '{' classVarDec* subroutineDec* '}'
        :return:
        """
        self._eat(JackTokenizer.CLASS)
        self._class_name = self._tokenizer.value()
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
            self.compile_class_vardec()
            self._class_var_dec_opt()

    def _subroutine_dec_opt(self):
        """
        Local recursive helper for the following optional
        GRAMMAR subroutineDec*
        :return:
        """
        subroutine_dec_str = [JackTokenizer.CONSTRUCTOR, JackTokenizer.FUNCTION, JackTokenizer.METHOD]
        self._symbol_table.start_subroutine()
        if self._tokenizer.has_more_tokens() and self._tokenizer.value() in subroutine_dec_str:
            if self._tokenizer.value() == JackTokenizer.METHOD:
                name = JackTokenizer.THIS
                type = self._class_name
                kind = SymbolTable.ARG
                self._symbol_table.define(name, type, kind)
                self._is_method = True
                self._is_constructor = False
            elif self._tokenizer.value() == JackTokenizer.CONSTRUCTOR:
                self._is_method = False
                self._is_constructor = True
            else:
                self._is_method = False
                self._is_constructor = False
            self.compile_subroutine()
            self._subroutine_dec_opt()

    def compile_class_vardec(self):
        """
        Compiles a static declaration or a field declaration
        Grammar: ('static' | 'field') type varName (',' varName)* ';'
        :return:
        """
        # refers to static/field
        kind = self._tokenizer.value()
        self._eat(self._tokenizer.value())
        types = [JackTokenizer.INT, JackTokenizer.CHAR, JackTokenizer.BOOLEAN]
        type = self._tokenizer.value()
        if self._tokenizer.has_more_tokens and self._tokenizer.value() in types:
            self._eat(self._tokenizer.value())
        else:
            # identifier for className
            self._eat(None)
        # identifier for varName
        name = self._tokenizer.value()
        self._eat(None)
        self._symbol_table.define(name, type, kind)
        self._var_name_opt(type, kind)
        self._eat(JackTokenizer.SEMICOLON)

    def _var_name_opt(self, type, kind):
        """
        Local recursive helper for the following optional
        GRAMMAR (',' varName)*
        :return:
        """
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.COMMA:
            self._eat(JackTokenizer.COMMA)
            # identifer for varName
            self._symbol_table.define(self._tokenizer.value(), type, kind)
            self._eat(None)
            self._var_name_opt(type, kind)

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
            if self._tokenizer.value() == JackTokenizer.VOID:
                self._is_void_function = True
            else:
                self._is_void_function = False
            self._eat(self._tokenizer.value())
        else:
            # identifer for className
            self._eat(None)
            self._is_void_function = False
        # identifier for subroutineName
        self._function_name = self._tokenizer.value()
        self._eat(None)
        self._eat(JackTokenizer.OPEN_BRACK)
        self.compile_parameterlist()
        self._eat(JackTokenizer.CLOSE_BRACK)
        self.compile_subroutine_body()
        # reset labels for every function
        self._ifid = -1
        self._whileid = -1

    def compile_subroutine_body(self):
        """
        Compiles the subroutine body
        Grammar: '{' varDec* statements '}'
        :return:
        """
        self._eat(JackTokenizer.OPEN_CURLY)
        self._var_dec_opt()
        nlocals = self._symbol_table.var_count(JackTokenizer.VAR)
        self._vmwriter.write_function("{c}.{m}".format(c=self._class_name, m=self._function_name), nlocals)
        if self._is_method:
            self._vmwriter.write_push(VMWriter.ARG, 0)
            self._vmwriter.write_pop(VMWriter.POINTER, 0)
        if self._is_constructor:
            nfields = self._symbol_table.var_count(JackTokenizer.FIELD)
            self._vmwriter.write_push(VMWriter.CONSTANT, nfields)
            self._vmwriter.write_call("Memory.alloc", 1)
            self._vmwriter.write_pop(VMWriter.POINTER, 0)
        self.compile_statements()
        self._eat(JackTokenizer.CLOSE_CURLY)

    def _var_dec_opt(self):
        """
        Local recursive helper for the following optional
        GRAMMAR (varDec)*
        :return:
        """
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.VAR:
            self.compile_vardec()
            self._var_dec_opt()

    def _var_opt(self, type, kind):
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.COMMA:
            self._eat(JackTokenizer.COMMA)
            self._symbol_table.define(self._tokenizer.value(), type, kind)
            self._eat(None)
            self._var_opt(type, kind)

    def _type_var_name_opt(self):
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.COMMA:
            self._eat(JackTokenizer.COMMA)
            if not self._compile_params():
                raise Exception("Token mismatch for paramList")
            self._type_var_name_opt()

    def compile_parameterlist(self):
        """
        Compiles a (possibly empty parameter list, not including the enclosing "()"
        Grammar: ((type varName) (',' type varName)*)?
        :return:
        """
        if self._compile_params():
            self._type_var_name_opt()

    def _compile_params(self):
        check = False
        kind = SymbolTable.ARG
        types = [JackTokenizer.INT, JackTokenizer.CHAR, JackTokenizer.BOOLEAN]
        if self._tokenizer.has_more_tokens() and self._tokenizer.value() in types:
            type = self._tokenizer.value()
            self._eat(self._tokenizer.value())
            name = self._tokenizer.value()
            self._eat(None)
            check = True
        elif self._tokenizer.has_more_tokens() and self._tokenizer.token_type() == JackTokenizer.IDENTIFIER:
            type = self._tokenizer.value()
            self._eat(None)
            name = self._tokenizer.value()
            self._eat(None)
            check = True
        if check:
            self._symbol_table.define(name, type, kind)
        return check

    def compile_vardec(self):
        """
        Compiles a var declaration
        Grammar: 'var' type varName (',' varName)* ';'
        :return:
        """
        kind = JackTokenizer.VAR
        self._eat(JackTokenizer.VAR)
        types = [JackTokenizer.INT, JackTokenizer.CHAR, JackTokenizer.BOOLEAN]
        type = self._tokenizer.value()
        if self._tokenizer.value() in types:
            self._eat(self._tokenizer.value())
        else:
            # identifer for className
            self._eat(None)
        # identifier for varName
        name = self._tokenizer.value()
        self._eat(None)
        self._symbol_table.define(name, type, kind)
        self._var_opt(type, kind)
        self._eat(JackTokenizer.SEMICOLON)

    def compile_statements(self):
        """
        Compiles a sequence of statements, not including the enclosing "{}"
        Grammar: letStatement | ifStatement | whileStatement | doStatement | returnStatement
        :return:
        """
        keyword_function_map = {
            JackTokenizer.LET: self.compile_let,
            JackTokenizer.IF: self.compile_if,
            JackTokenizer.WHILE: self.compile_while,
            JackTokenizer.DO: self.compile_do,
            JackTokenizer.RETURN: self.compile_return
        }
        if self._tokenizer.has_more_tokens() and self._tokenizer.value() in keyword_function_map:
            keyword_function_map[self._tokenizer.value()]()
            # reset to 0
            self._no_arguments = 0
            self.compile_statements()

    def compile_do(self):
        """
        Compiles a do statement
        Grammar: 'do' subroutineCall ';'
        :return:
        """
        method_call = False
        self._eat(JackTokenizer.DO)
        variable = self._tokenizer.value()
        self._eat(None)
        if not self._tokenizer.has_more_tokens:
            raise Exception("No tokens found after do keyword")
        # dealing with subroutineCall
        if self._tokenizer.value() == JackTokenizer.OPEN_BRACK:
            # is direct method call
            method_call = True
            # pushing this to stack
            self._vmwriter.write_push(VMWriter.POINTER, 0)
            self._eat(JackTokenizer.OPEN_BRACK)
            self.compile_expressionlist()
            self._eat(JackTokenizer.CLOSE_BRACK)
            variable = "{c1}{d}{v}".format(c1=self._class_name, d=JackTokenizer.DOT, v=variable)
        elif self._tokenizer.value() == JackTokenizer.DOT:
            result = self._symbol_table.type_of(variable)
            if result is not None:
                # is a method call using object ref, so first argument is object ref
                method_call = True
                # push object ref to stack
                self._push_pop_variable(variable, True)
                variable = result
            self._eat(JackTokenizer.DOT)
            variable = "{v1}{d}{v2}".format(v1=variable, d=JackTokenizer.DOT, v2=self._tokenizer.value())
            self._eat(None)
            self._eat(JackTokenizer.OPEN_BRACK)
            self.compile_expressionlist()
            self._eat(JackTokenizer.CLOSE_BRACK)
        else:
            raise Exception("Invalid do syntax")
        #### end of subroutineCall
        self._eat(JackTokenizer.SEMICOLON)
        if method_call:
            self._no_arguments = self._no_arguments + 1
        self._vmwriter.write_call(variable, self._no_arguments)
        # since do statement, discard var in top of stack
        self._vmwriter.write_pop(VMWriter.TEMP, 0)

    def compile_let(self):
        """
        Compiles a let statement
        Grammar: 'let' varName ('[' expression ']')? '=' expression ';'
        :return:
        """
        # refers to varName[expression]
        is_array = False
        self._eat(JackTokenizer.LET)
        variable = self._tokenizer.value()
        self._eat(None)
        if not self._tokenizer.has_more_tokens():
            raise Exception("Invalid let syntax")
        ######## optional ############
        # refers to array access a[i]
        if self._tokenizer.value() == JackTokenizer.OPEN_SQUARE:
            _is_array = True
            self._eat(JackTokenizer.OPEN_SQUARE)
            self.compile_expression()
            self._eat(JackTokenizer.CLOSE_SQUARE)
            self._push_pop_variable(variable, True)
            self._vmwriter.write_arithmetic(VMWriter.ADD)
        #############################
        else:
            _is_array = False
        self._eat(JackTokenizer.EQUAL)
        self._push_ops(JackTokenizer.OPEN_BRACK)
        self.compile_expression()
        self._write_ops()
        if not _is_array:
            # poping variable from stack
            self._push_pop_variable(variable, False)
        self._eat(JackTokenizer.SEMICOLON)
        if _is_array:
            # align the that pointer
            self._vmwriter.write_pop(VMWriter.TEMP, 0)
            self._vmwriter.write_pop(VMWriter.POINTER, 1)
            self._vmwriter.write_push(VMWriter.TEMP, 0)
            self._vmwriter.write_pop(VMWriter.THAT, 0)

    def compile_while(self):
        """
        Compiles a while statement using following grammar mentioned below
        Grammar: 'while' '(' expression ')' '{' statements '}'
        :return:
        """
        while_id = self._get_whileid()
        l1 = "WHILE_EXP{u}".format(u=while_id)
        l2 = "WHILE_END{u}".format(u=while_id)
        self._vmwriter.write_label(l1)
        self._eat(JackTokenizer.WHILE)
        self._eat(JackTokenizer.OPEN_BRACK)
        self._push_ops(JackTokenizer.OPEN_BRACK)
        self.compile_expression()
        self._write_ops()
        self._vmwriter.write_arithmetic(VMWriter.NOT)
        self._vmwriter.write_if(l2)
        self._eat(JackTokenizer.CLOSE_BRACK)
        self._eat(JackTokenizer.OPEN_CURLY)
        self.compile_statements()
        self._vmwriter.write_goto(l1)
        self._vmwriter.write_label(l2)
        self._eat(JackTokenizer.CLOSE_CURLY)

    def compile_return(self):
        """
        Compiles a return statement
        Grammar: 'return' expression? ';'
        :return:
        """
        self._eat(JackTokenizer.RETURN)
        self._ops_stack.push(JackTokenizer.OPEN_BRACK)
        ######OPTONAL#####################
        if self._tokenizer.has_more_tokens() and self._tokenizer.value() != JackTokenizer.SEMICOLON:
            self.compile_expression()
        self._eat(JackTokenizer.SEMICOLON)
        if self._is_void_function:
            self._vmwriter.write_push(VMWriter.CONSTANT, 0)
        self._write_ops()
        self._vmwriter.write_return()

    def compile_if(self):
        """
        Compiles an if statement, possibly with a trailing else clause
        Grammar: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        :return:
        """
        if_id = self._get_ifid()
        l1 = 'IF_TRUE{u}'.format(u=if_id)
        l2 = 'IF_FALSE{u}'.format(u=if_id)
        l3 = 'IF_END{u}'.format(u=if_id)
        self._eat(JackTokenizer.IF)
        self._eat(JackTokenizer.OPEN_BRACK)
        self._push_ops(JackTokenizer.OPEN_BRACK)
        self.compile_expression()
        self._write_ops()
        self._vmwriter.write_if(l1)
        self._vmwriter.write_goto(l2)
        self._vmwriter.write_label(l1)
        self._eat(JackTokenizer.CLOSE_BRACK)
        self._eat(JackTokenizer.OPEN_CURLY)
        self.compile_statements()
        self._eat(JackTokenizer.CLOSE_CURLY)
        ######## optional ############
        if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.ELSE:
            self._vmwriter.write_goto(l3)
            self._vmwriter.write_label(l2)
            self._eat(JackTokenizer.ELSE)
            self._eat(JackTokenizer.OPEN_CURLY)
            self.compile_statements()
            self._eat(JackTokenizer.CLOSE_CURLY)
            self._vmwriter.write_label(l3)
            #############################
        else:
            self._vmwriter.write_label(l2)

    def compile_expression(self):
        """
        Compiles an expression
        :return:
        Grammar: term (op term)*
        """
        self.compile_term()
        self._ops_term_opt()

    def _ops_term_opt(self):
        if not self._tokenizer.has_more_tokens():
            return
        binary_ops = [
            JackTokenizer.PLUS,
            JackTokenizer.MINUS,
            JackTokenizer.NOT_EQUAL,
            JackTokenizer.EQUAL,
            JackTokenizer.LESS,
            JackTokenizer.GREATER,
            JackTokenizer.AND,
            JackTokenizer.OR,
            JackTokenizer.DIVIDE,
            JackTokenizer.STAR
        ]

        if self._tokenizer.value() in binary_ops:
            self._ops_stack.push(self._tokenizer.value())
            self._eat(self._tokenizer.value())
            self.compile_term()
            self._ops_term_opt()

    def _push_ops(self, symbol):
        """
        Utility method to symbols(operands and curly braces) to stack
        :param symbol:
        :return:
        """
        self._ops_stack.push(symbol)

    def _write_ops(self):
        """
        Utility method to generate ops from stack
        :return:
        """
        # popping out operands after expression
        ops_map = {
            JackTokenizer.PLUS: VMWriter.ADD,
            JackTokenizer.MINUS: VMWriter.SUB,
            JackTokenizer.UNARY_MINUS: VMWriter.NEG,
            JackTokenizer.NOT_EQUAL: VMWriter.NOT,
            JackTokenizer.EQUAL: VMWriter.EQ,
            JackTokenizer.LESS: VMWriter.LT,
            JackTokenizer.GREATER: VMWriter.GT,
            JackTokenizer.AND: VMWriter.AND,
            JackTokenizer.OR: VMWriter.OR,
            JackTokenizer.DIVIDE: "Math.divide",
            JackTokenizer.STAR: "Math.multiply"
        }
        while not self._ops_stack.is_empty():
            if self._ops_stack.peek() == JackTokenizer.OPEN_BRACK:
                self._ops_stack.pop()
                break
            if self._ops_stack.peek() not in (JackTokenizer.DIVIDE, JackTokenizer.STAR):
                self._vmwriter.write_arithmetic(ops_map[self._ops_stack.pop()])
            else:
                self._vmwriter.write_call(ops_map[self._ops_stack.pop()], 2)

    def _eval_array_expressions(self, variable):
        """
        Utility method to deal with array access, a[i] in expressions
        Usage: accessing array element, a[i]
        :return:
        """
        # dealing with array access a[i] in expression
        self._eat(JackTokenizer.OPEN_SQUARE)
        self._push_ops(JackTokenizer.OPEN_BRACK)
        # print out expression i first
        self.compile_expression()
        self._eat(JackTokenizer.CLOSE_SQUARE)
        self._write_ops()
        # then print out a
        self._push_pop_variable(variable, True)
        # sets the base address of a[i] in top of stack
        self._vmwriter.write_arithmetic(VMWriter.ADD)
        # set the that pointer to base address of a[i]
        self._vmwriter.write_pop(VMWriter.POINTER, 1)
        self._vmwriter.write_push(VMWriter.THAT, 0)

    def _eval_subroutines(self):
        """
        Utility method to deal with subroutine evaluation, var()
        Usage: method call, varName(exp1, exp2, .. expN)
        :return:
        """
        self._eat(JackTokenizer.OPEN_BRACK)
        self.compile_expressionlist()
        self._eat(JackTokenizer.CLOSE_BRACK)

    def compile_term(self):
        """
        Compiles a term
        :return:
        Grammar: integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' |
                 subroutineCall  | unaryOp term
        """
        if not self._tokenizer.has_more_tokens():
            raise Exception("Failure to compile term")
        if self._tokenizer.token_type() == JackTokenizer.INT_CONSTANT:
            self._vmwriter.write_push(VMWriter.CONSTANT, self._tokenizer.value())
            self._eat(self._tokenizer.value())
        elif self._tokenizer.token_type() == JackTokenizer.STRING_CONSTANT:
            # need to revisit
            length = len(self._tokenizer.value())
            self._vmwriter.write_push(VMWriter.CONSTANT, length)
            self._vmwriter.write_call('String.new', 1)
            for s in self._tokenizer.value():
                self._vmwriter.write_push(VMWriter.CONSTANT, ord(s))
                self._vmwriter.write_call('String.appendChar', 2)
            self._eat(self._tokenizer.value())
        elif self._tokenizer.value() == JackTokenizer.TRUE:
            self._vmwriter.write_push(VMWriter.CONSTANT, 0)
            self._vmwriter.write_arithmetic(VMWriter.NOT)
            self._eat(self._tokenizer.value())
        elif self._tokenizer.value() == JackTokenizer.FALSE or self._tokenizer.value() == JackTokenizer.NULL:
            self._vmwriter.write_push(VMWriter.CONSTANT, 0)
            self._eat(self._tokenizer.value())
        elif self._tokenizer.value() == JackTokenizer.THIS:
            self._vmwriter.write_push(VMWriter.POINTER, 0)
            self._eat(self._tokenizer.value())
        elif self._tokenizer.token_type() == JackTokenizer.IDENTIFIER:
            variable = self._tokenizer.value()
            self._eat(None)
            if self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.OPEN_SQUARE:
                # dealing with array access a[i] in expression
                self._eval_array_expressions(variable)
            #### dealing with subroutineCall
            elif self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.OPEN_BRACK:
                #### setx()
                self._eval_subroutines()
            elif self._tokenizer.has_more_tokens and self._tokenizer.value() == JackTokenizer.DOT:
                ####  a.setx()
                is_method = False
                self._eat(JackTokenizer.DOT)
                result = self._symbol_table.type_of(variable)
                if result is not None:
                    is_method = True
                    self._push_pop_variable(variable, True)
                    variable = result
                variable = "{v}{d}{va}".format(v=variable, d=JackTokenizer.DOT, va=self._tokenizer.value())
                self._eat(None)
                self._eval_subroutines()
                #### end of subroutineCall
                if is_method:
                    self._no_arguments = self._no_arguments + 1
                self._vmwriter.write_call(variable, self._no_arguments)
            else:
                # dealing with accessing variables through let statement
                self._push_pop_variable(variable, True)
        elif self._tokenizer.value() == JackTokenizer.OPEN_BRACK:
             # dealing with (expression)
            self._eat(JackTokenizer.OPEN_BRACK)
            self._push_ops(JackTokenizer.OPEN_BRACK)
            self.compile_expression()
            self._eat(JackTokenizer.CLOSE_BRACK)
            self._write_ops()
        # dealing with unary ops
        elif self._tokenizer.value() == JackTokenizer.MINUS:
            self._push_ops(JackTokenizer.UNARY_MINUS)
            self._eat(self._tokenizer.value())
            self.compile_term()
        elif self._tokenizer.value() == JackTokenizer.NOT_EQUAL:
            self._push_ops(self._tokenizer.value())
            self._eat(self._tokenizer.value())
            self.compile_term()
        # end of unary ops
        else:
            raise Exception("Not a valid term")

    def _push_pop_variable(self, variable, push):
        """
        Utility method to push/pop variable defined in symbol table
        :param variable:
        :param push:
        :return:
        """
        index = self._symbol_table.index_of(variable)
        kind = self._symbol_table.kind_of(variable)
        if index is None:
            raise Exception("Identifier {v} used which is not found in scope".format(v=variable))
        kind_segment_map = {
            JackTokenizer.FIELD: VMWriter.THIS,
            JackTokenizer.STATIC: VMWriter.STATIC,
            JackTokenizer.VAR: VMWriter.LOCAL,
            SymbolTable.ARG: VMWriter.ARG
        }
        if push:
            self._vmwriter.write_push(kind_segment_map[kind], index)
        else:
            self._vmwriter.write_pop(kind_segment_map[kind], index)

    def _setup_compile_expression_stack(self):
        self._push_ops(JackTokenizer.OPEN_BRACK)
        self.compile_expression()

    def compile_expressionlist(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions
        :return:
        Grammar: (expression (',' expression)*)?
        """
        if not self._tokenizer.has_more_tokens():
            raise Exception("Expression list closing token not {c} ".format(c=JackTokenizer.CLOSE_BRACK))
        if self._tokenizer.value() != JackTokenizer.CLOSE_BRACK:
            self._no_arguments = 1
            self._setup_compile_expression_stack()
            self._expression_opt()

    def _expression_opt(self):
        """
        Local recursive helper to check for expressions
        :return:
        """
        # popping out operands from stack
        self._write_ops()
        if self._tokenizer.has_more_tokens() and self._tokenizer.value() == JackTokenizer.COMMA:
            self._no_arguments = self._no_arguments + 1
            self._eat(JackTokenizer.COMMA)
            self._setup_compile_expression_stack()
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
                "Actual Token value {t} does not match Expected value {s}".format(t=self._tokenizer.value(),
                                                                                  s=string))
        if self._tokenizer.has_more_tokens():
            self._tokenizer.advance()


class SymbolTable:
    """
    Provides a symbol table abstraction. The symbol table associates the identifier names found in the program with
    identifier properties needed for compilation: type, kind and running index. The symbol table for Jack programs has
    two nested scopes (class/subroutine)
    """
    # class-scope types from JackTokenizer
    # STATIC = "static"
    # FIELD = "field"
    # method-scope types
    ARG = "argument"

    # VAR = "var" from JackTokenizer

    def __init__(self):
        """
        Creates new empty symbol table
        """
        self._class_table = {}
        self._class_table_running_count = {JackTokenizer.STATIC: 0, JackTokenizer.FIELD: 0}
        self._subroutine_table = {}
        self._subroutine_table_running_count = {JackTokenizer.VAR: 0, SymbolTable.ARG: 0}

    def start_subroutine(self):
        """
        Starts a new subroutine scope / resets the subroutine symbol table
        :return:
        """
        self._subroutine_table = {}
        self._subroutine_table_running_count = {JackTokenizer.VAR: 0, SymbolTable.ARG: 0}

    def define(self, name, type, kind):
        """
        defines a new identifier of a given name, type and kind and assigns it a running index.
        STATIC and FIELD identifers have a class scope while ARG and VAR identifiers have a subroutine scope
        :param name:
        :param type:
        :param kind:
        :return:
        """
        if kind in (JackTokenizer.STATIC, JackTokenizer.FIELD):
            self._class_table[name] = (type, kind, self._class_table_running_count[kind])
            self._class_table_running_count[kind] = self._class_table_running_count[kind] + 1
        else:
            self._subroutine_table[name] = (type, kind, self._subroutine_table_running_count[kind])
            self._subroutine_table_running_count[kind] = self._subroutine_table_running_count[kind] + 1

    def var_count(self, kind):
        """
        Returns the number of variables of the given kind already defined in the current scope
        :param kind:
        :return:
        """
        if kind in self._subroutine_table_running_count:
            return self._subroutine_table_running_count[kind]
        elif kind in self._class_table_running_count:
            return self._class_table_running_count[kind]
        else:
            raise Exception("{f} not defined".format(f=kind))

    def kind_of(self, name):
        """
        Returns the kind of the named identifier in th current scope.
        If the identifier is unknown , the current scope is NONE
        :param name:
        :return:
        """
        return self._get_attr(name, 1)

    def type_of(self, name):
        """
        Returns the type of the named identifier in th current scope.
        :param name:
        :return:
        """
        return self._get_attr(name, 0)

    def index_of(self, name):
        """
        Returns the index assigned to the named identifer.
        :param name:
        :return:
        """
        return self._get_attr(name, 2)

    def _get_attr(self, name, index):
        if name in self._class_table:
            return self._class_table[name][index]
        if name in self._subroutine_table:
            return self._subroutine_table[name][index]
        return None


class VMWriter:
    """
    Output module for generating VM code
    """
    # vm memory segments
    ARG = "argument"
    POINTER = "pointer"
    CONSTANT = "constant"
    STATIC = "static"
    THIS = "this"
    THAT = "that"
    LOCAL = "local"
    TEMP = "temp"
    # vm arithmetic operations
    ADD = "add"
    SUB = "sub"
    NEG = "neg"
    # vm logical operations
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    AND = "and"
    OR = "or"
    NOT = "not"

    def __init__(self, file_name):
        """
        Creates a new file and prepares it for writing
        """
        self._output = open(file_name, "w")

    def write_push(self, segment, index):
        """
        Writes a VM push command
        :param segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        :param index: int
        :return:
        """
        self._output.write('push {s} {i}'.format(s=segment, i=index))
        self._output.write('\n')

    def write_pop(self, segment, index):
        """
        Writes a VM pop command
        :param segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        :param index: int
        :return:
        """
        self._output.write('pop {s} {i}'.format(s=segment, i=index))
        self._output.write('\n')

    def write_arithmetic(self, command):
        """
        Writes a VM arithmetic command
        :param command: ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT
        :return:
        """
        self._output.write(command)
        self._output.write('\n')

    def write_label(self, label):
        """
        Writes a VM label command
        :param label: String
        :return:
        """
        self._output.write('label {l}'.format(l=label))
        self._output.write('\n')

    def write_goto(self, label):
        """
        Writes a VM goto command
        :param label:
        :return:
        """
        self._output.write('goto {l}'.format(l=label))
        self._output.write('\n')

    def write_if(self, label):
        """
        Writes a VM if-goto command
        :param label:
        :return:
        """
        self._output.write('if-goto {l}'.format(l=label))
        self._output.write('\n')

    def write_call(self, name, nArgs):
        """
        Writes a VM call command
        :param name:
        :param nArgs:
        :return:
        """
        self._output.write('call {n} {a}'.format(n=name, a=nArgs))
        self._output.write('\n')

    def write_function(self, name, nlocals):
        """
        Writes a VM function command
        :param name:
        :param nlocals:
        :return:
        """
        self._output.write('function {n} {a}'.format(n=name, a=nlocals))
        self._output.write('\n')

    def write_return(self):
        """
        Writes a VM return command
        :return:
        """
        self._output.write('return')
        self._output.write('\n')

    def close(self):
        """
        Closes the output file
        :return:
        """
        self._output.close()


if __name__ == '__main__':
    """
    Entry point of program for execution
    """
    JackCompiler.check_dir()
