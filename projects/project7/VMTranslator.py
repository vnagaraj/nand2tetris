import sys
import re
import os


class Parser:
    """
    Handles the parsing of a single .vm file and encapsulates access to the input code
    Reads VM commands, parses them and provides convenient access to the components.
    In addition it removes all white spaces and comments
    """
    # command types
    C_ARITHMETIC = "c_arithmetic"
    C_PUSH = "c_push"
    C_POP = "c_pop"
    IGNORE = "ignore"
    INVALID = "invalid"
    # arithmetic binary operations
    ADD = "add"
    SUB = "sub"
    AND = "and"
    OR = "or"
    # arithmetic unary operations
    NEG = "neg"
    NOT = "not"
    # arithmetic logical operatiions
    EQ = "eq"
    LT = "lt"
    GT = "gt"
    # virtual memory segments
    CONSTANT = "constant"
    POINTER = "pointer"
    LOCAL = "local"
    STATIC = "static"
    THIS = "this"
    THAT = "that"
    TEMP = "temp"
    ARGUMENT = "argument"

    incr = 0

    def __init__(self, file_name):
        """
        Opens the input file/stream for parsing
        """
        self._lines = list()
        self._current_inst = -1  # initially no current command
        with open(file_name, 'r') as f:
            self._lines = f.readlines()
        self._line = self._lines[self._current_inst].strip()

    def has_more_commands(self):
        """
        Are there more commands to the input

        :return:
        Returns true if there are more commands, false otherwise
        """
        return self._current_inst < len(self._lines) - 1

    def advance(self):
        """
        Reads the next command from input and makes it the current command
        Should only be called only if has_more_commands returns true

        :return:
        Returns pointer to the next command
        """
        self._current_inst += 1
        self._line = self._lines[self._current_inst].strip()

    def command_type(self):
        """
        C_ARITHMETIC for add/sub/neg/eg/gt/lt/and/or/not
        C_PUSH for PUSH
        C_POP for POP
        Ignore incase of whitespaces or comments (//)

        :return:
        Returns the type of the current VM command
        """
        if self._is_push_command():
            command_type = Parser.C_PUSH
        elif self._is_pop_command():
            command_type = Parser.C_POP
        elif self._is_arithmetic_command():
            command_type = Parser.C_ARITHMETIC
        elif self._is_comment_line() or self._is_blank_line():
            command_type = Parser.IGNORE
        else:
            command_type = Parser.INVALID
        return command_type

    def arg1(self):
        """
        Returns the first argument of the current command.
        In case of C_ARITHMETIC the command itself(add, sub, etc) should be returned
        Should not be called if the current command is C_RETURN
        :return:
        """
        if self.command_type() == Parser.C_PUSH or self.command_type() == Parser.C_POP:
            arg1 = self._line.split()[1]
        elif self.command_type() == Parser.C_ARITHMETIC:
            arg1 = self._line.split()[0]
        else:
            raise Exception("Not to be invoked with any other command")
        return arg1

    def arg2(self):
        """
        Returns the second argument of the current command.
        Should be called if the current command is C_PUSH, C_POP, C_FUNCTION, C_CALL
        :return:
        """
        if self.command_type() == Parser.C_PUSH or self.command_type() == Parser.C_POP:
            arg1 = self._line.split()[2]
        else:
            raise Exception("Not to be invoked with any other command")
        return arg1

    def _is_push_command(self):
        """
        Push command format
        push local 0
        :return:
        """
        return self._match_memory_pattern("push")

    def _is_pop_command(self):
        """
        Pop command format
        pop local 12
        :return:
        """
        return self._match_memory_pattern("pop")

    def _is_arithmetic_command(self):
        """
        Arithmetic command format
        eg: add
        :return:
        """
        arithmetic_keywords = [Parser.ADD, Parser.SUB, Parser.NEG, Parser.EQ, Parser.GT, Parser.LT, Parser.AND,
                               Parser.OR, Parser.NOT]
        for keyword in arithmetic_keywords:
            pattern = re.compile(r"^(\s)*{k}(\s//(.)*)*$".format(k=keyword))
            if pattern.search(self._line):
                return True
        return False

    def _is_comment_line(self):
        """
        Any line starting with // with optional blank at beginning is comment line
        :return:
        """
        pattern = re.compile(r"^(\s)*(//)+")
        return pattern.search(self._line)

    def _is_blank_line(self):
        """
        Any line starting with empty white space
        :return:
        """
        pattern = re.compile(r"^(\s)*$")
        return pattern.search(self._line)

    def _match_memory_pattern(self, command_prefix):
        memory_segments = [Parser.ARGUMENT, Parser.LOCAL, Parser.STATIC, Parser.CONSTANT, Parser.THIS, Parser.THAT, Parser.POINTER, Parser.TEMP]
        for segment in memory_segments:
            pattern = re.compile(r"^(\s)*{c}(\s)+{s}(\s)+(\d)+(\s//(.)*)*$".format(c=command_prefix, s=segment))
            if pattern.search(self._line):
                return True
        return False


class CodeWriter:
    """
    Translates VM commands into Hack assembly code
    """

    def __init__(self, output_file):
        """
        Opens the output file/stream and gets ready to write into it
        :param output_file:
        """
        self.file = open(output_file, "w")

    def set_filename(self, file_name):
        """
        Informs the code writer that the translation of a new VM file is started
        :param file_name:
        :return:
        """

    def write_arithmetic(self, command):
        """
        Writes the assembly code that is the translation of the given arithmetic command
        :param command:
        :return:
        """
        option = command.split(',')[1]
        binary_op = [Parser.ADD, Parser.SUB, Parser.AND, Parser.OR, Parser.EQ, Parser.LT, Parser.GT]
        if option in binary_op:
            init = self._decr_stack_pointer() + self._set_D("SP", "M") + self._decr_stack_pointer()
        else:
            init = self._decr_stack_pointer()
        if option == Parser.ADD:
            spec = self._set_stack("D+M")
        if option == Parser.SUB:
            spec = self._set_stack("M-D")
        if option == Parser.AND:
            spec = self._set_stack("D&M")
        if option == Parser.OR:
            spec = self._set_stack("D|M")
        if option == Parser.NEG:
            spec = self._set_stack("-M")
        if option == Parser.NOT:
            spec = self._set_stack("!M")
        if option == Parser.EQ:
            spec = self._set_logical_op("JEQ", Parser.incr)
            Parser.incr += 1
        if option == Parser.LT:
            spec = self._set_logical_op("JGT", Parser.incr)
            Parser.incr += 1
        if option == Parser.GT:
            spec = self._set_logical_op("JLT", Parser.incr)
            Parser.incr += 1
        final = self._incr_stack_pointer()
        return self._print(init + spec + final)

    def write_pushpop(self, command):
        """
        Writes the assembly code that is the translation of the given command where command is
        C_PUSH or C_POP
        :param command:
        :return:
        """
        commands = command.split(',')
        command_type = commands[0]
        vir_mem = commands[1]
        offset = commands[2]
        file_name = commands[3]
        vm_assembly_map = {Parser.LOCAL: "LCL", Parser.ARGUMENT: "ARG", Parser.THIS: "THIS", Parser.THAT: "THAT"}
        if command_type == Parser.C_PUSH and vir_mem in vm_assembly_map:
            # D register gets value of the vir mem seg
            c1 = self._set_D_A(offset)
            c2 = ["@{s}".format(s=vm_assembly_map[vir_mem]), "A=D+M", "D=M"]
            # stack gets value from D
            c3 = self._set_stack("D")
            # incrementing stack to point to next address
            c4 = self._incr_stack_pointer()
            return self._print(c1 + c2 + c3 +c4)
        elif command_type == Parser.C_PUSH and vir_mem == Parser.CONSTANT:
            # assign stack to have the constant value
            c1 = self._set_D_A(offset)
            c2 = self._set_stack("D")
            # incrementing stack to point to next address
            c3 = self._incr_stack_pointer()
            return self._print(c1 + c2 + c3)
        elif command_type == Parser.C_PUSH and vir_mem == Parser.TEMP:
            offset = str(5 + int(offset))
            c1 = ["@{o}".format(o=offset), "D=M"]
            # stack gets value from D
            c2 = self._set_stack("D")
            # incrementing stack to point to next address
            c3 = self._incr_stack_pointer()
            return self._print(c1 + c2 + c3)
        elif command_type == Parser.C_PUSH and vir_mem == Parser.STATIC:
            paths = file_name.split("/")
            file_name = paths[len(paths)-1]
            offset = '.'.join([file_name, offset])
            c1 = ["@{o}".format(o=offset), "D=M"]
            # stack gets value from D
            c2 = self._set_stack("D")
            # incrementing stack to point to next address
            c3 = self._incr_stack_pointer()
            return self._print(c1 + c2 + c3)
        elif command_type == Parser.C_PUSH and vir_mem == Parser.POINTER:
            offset_dict = {"0": "THIS", "1": "THAT"}
            val = offset_dict[offset]
            # *SP = THIS/THAT
            c1 = ["@{v}".format(v=val), "D=M"]
            c2 = self._set_stack("D")
            # incrementing stack to point to next address
            c3 = self._incr_stack_pointer()
            return self._print(c1 + c2 + c3)
        elif command_type == Parser.C_POP and vir_mem in vm_assembly_map:
            # decrement stack pointer and place contents of the stack in D register
            c1 = self._decr_stack_pointer()
            # D now stores the RAM address of where info needs to be stored
            c2 = ["@{o}".format(o=offset), "D=A", "@{s}".format( s=vm_assembly_map[vir_mem]),"D=D+M"]
            # D stores address where info needs to be stored  and value of stack
            c3 = ["@SP", "A=M", "D=D+M"]
            # go to address stored in previous M
            c4 = ["A=D-M"]
            # place value in address from D and A
            c5 = ["M=D-A"]
            return self._print(c1 + c2 + c3 + c4 + c5)
        elif command_type == Parser.C_POP and vir_mem == Parser.TEMP:
            # decrement stack pointer and place contents of the stack in D register
            c1 = self._decr_stack_pointer()
            c2 = ["@SP", "A=M", "D=M"]
            offset = str(5 + int(offset))
            # store in temp segment from D register
            c3 = ["@{o}".format(o=offset), "M=D"]
            return self._print(c1 + c2 + c3)
        elif command_type == Parser.C_POP and vir_mem == Parser.STATIC:
            # decrement stack pointer and place contents of the stack in D register
            c1 = self._decr_stack_pointer()
            c2 = ["@SP", "A=M", "D=M"]
            paths = file_name.split("/")
            file_name = paths[len(paths)-1]
            offset = '.'.join([file_name, offset])
            # store in temp segment from D register
            c3 = ["@{o}".format(o=offset), "M=D"]
            return self._print(c1 + c2 + c3)
        elif command_type == Parser.C_POP and vir_mem == Parser.POINTER:
            # SP --
            # THIS/THAT = *SP
            offset_dict = {"0": "THIS", "1": "THAT"}
            val = offset_dict[offset]
            # decrement stack pointer and place contents of the stack in D register
            c1 = self._decr_stack_pointer()
            c2 = ["@SP", "A=M", "D=M"]
            c3 = ["@{v}".format(v= val), "M=D"]
            return self._print(c1 + c2 + c3)
        raise Exception("Invalid push/pop command")

    def _print(self, command):
        for c in command:
            self.file.write(c + "\n")

    def close(self):
        self.file.close()

    def _incr_stack_pointer(self):
        """
        SP = SP +1
        """
        return ["@SP", "M=M+1"]

    def _decr_stack_pointer(self):
        """
        SP = SP -1
        """
        return ["@SP", "M=M-1"]

    def _set_D(self, symbol, address):
        """
        Set the D register of the RAM from the symbol pointer
        @:symbol: SP/LCL/ARG/THIS/THAT
        D = *symbol
        """
        return ["@{s}".format(s=symbol), "A={a}".format(a=address), "D=M"]

    def _set_stack(self, val):
        """
        Set stack pointer to any constant
        *SP = const
        """
        return ["@SP", "A=M", "M={v}".format(v=val)]

    def _set_D_A(self, val):
        """
        Set the D register of the RAM from the A register
        D = A
        """
        return ["@{v}".format(v=val), "D=A"]

    def _set_logical_op(self, condition, incr):
        """
        logical (EQ/LT/GT) specific commands
        :return:
        """
        c1 = ["@SP", "A=M", "D=D-M"]
        c2 = ["@TRUE{i}" .format(i=incr)]
        c3 = ["D;{c}".format(c=condition)]
        c4 = ["(FALSE{i})".format(i=incr)]
        c5 = self._set_stack(0)
        c6 = ["@ACOND{i}".format(i=incr)]
        c7 = ["0;JMP"]
        c8 = ["(TRUE{i})".format(i=incr)]
        c9 = self._set_stack(-1)
        c10 = ["(ACOND{i})".format(i=incr)]
        return c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 +c10

    def _set_virmem_D(self, virmem, offset):
        """
        *virmem = D
        """
        return ["@{o}", "D=A", "@{a}".format(a=virmem), "A=M+D".format(o=offset), "M=D"]

    def set_end(self):
        return self._print(["(END)", "@END", "0;JMP" ])


class Driver:
    """
    Class to drive program execution

    """
    @staticmethod
    def check_dir():
        path = str(sys.argv[1])
        if os.path.isfile(path):
            if path.endswith(".vm"):
                Driver.start(path)
            else:
                raise Exception("Filename should end with .vm")
        elif os.path.isdir(path):
            for filename in os.listdir(path):
                if filename.endswith(".vm"):
                    file = os.path.join(path, filename)
                    Driver.start(file)
        else:
            raise Exception("Not a valid file/path")

    @staticmethod
    def start(file_name):
        p = Parser(file_name)
        index = file_name.find(".")
        new_file = file_name[0:index] + ".asm"
        c = CodeWriter(new_file)
        instruction_count = 0
        # first pass - adding program labels to the symbol table
        while p.has_more_commands():
            p.advance()
            if p.command_type() == Parser.C_PUSH or p.command_type() == Parser.C_POP:
                command = [p.command_type(), p.arg1(), p.arg2(), file_name[0:index]]
                c.write_pushpop(','.join(command))
            elif p.command_type() == Parser.C_ARITHMETIC:
                command = [p.command_type(), p.arg1()]
                c.write_arithmetic(','.join(command))
            elif p.command_type() == Parser.IGNORE:
                pass
            else:
                raise Exception("Invalid syntax")
        c.set_end()

if __name__ == '__main__':
    """
    Entry point of program for execution
    """
    Driver.check_dir()
