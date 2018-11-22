import sys
import numpy


class Parser:
    """
    Encapsulates access to the input code.
    Read and assembly language command, parses it and provides convenient access to the command's components(fields and symbols)
    """
    # class constants
    A_COMMAND = "a_instruction"
    C_COMMAND = "c_instruction"
    L_COMMAND = "label_instruction"
    IGNORE = "ignore"

    def __init__(self, file_name):
        """
        Opens the input file/stream for parsing
        """
        self._lines = list()
        self._current_inst = 0
        with open(file_name, 'r') as f:
            self._lines = f.readlines()
        self._line = self._lines[self._current_inst].strip()

    def command_type(self):
        """
        A_COMMAND for @xxx instruction
        L_COMMAND for (xxx) label
        C_COMMAND for dest=comp;jump
        Ignore incase of whitespaces or comments (//)

        :return:
        Returns type of current command
        """

        c_index = self._line.find('//')
        a_index = self._line.find('@')
        l_o_index = self._line.find('(')
        l_c_index = self._line.find(')')
        if c_index == -1:
            c_index = sys.maxint
        if len(self._line) == 0:
            # empty line with white spacesk
            return Parser.IGNORE
        # in case of inline comments/no comments in text
        if a_index != -1 and a_index < c_index:
            return Parser.A_COMMAND
        # no comments in text
        if l_o_index != -1 and l_c_index != -1 and l_o_index < l_c_index and l_o_index < c_index:
            return Parser.L_COMMAND
        words = self._line.split()
        if words[0].find('//') == -1:
            return Parser.C_COMMAND
        return Parser.IGNORE

    def advance(self):
        """
        Reads the next command from input and makes it the current command
        Should only be called only if has_more_commands returns true

        :return:
        Returns pointer to the next command
        """
        self._current_inst += 1
        self._line = self._lines[self._current_inst].strip()

    def has_more_commands(self):
        """
        Are there more commands to the input

        :return:
        Returns true if there are more commands, false otherwise
        """
        return self._current_inst < len(self._lines) - 1

    def symbol(self):
        """
        Should only be called when command_type() returns A_COMMAND

        :return:
        Returns the symbol of the current command(@xxx/(xxx))
        """
        if self.command_type() == Parser.A_COMMAND:
            a_index = self._line.find('@')
            symbol = self._line[a_index + 1:]
        else:
            l_o_index = self._line.find('(')
            l_c_index = self._line.find(')')
            symbol = self._line[l_o_index + 1:l_c_index]
        return symbol

    def dest(self):
        """
        Should only be called when command_type() returns C_COMMAND

        :return:
        Returns the dest mneumonic in the current C-command(8 possibilities)
        """
        index = self._line.find("=")
        if index == -1:
            return None
        words = self._line[0: index].split()
        for w in words:
            if len(w) != 0:
                return w

    def comp(self):
        """
        Should only be called when command_type() returns C_COMMAND

        :return:
        Returns the comp mneumonic in the current C-command(28 possibilities)
        """
        index_e = self._line.find("=")
        index_j = self._line.find(";")
        if index_e == -1 and index_j == -1:
            string = self._line
        elif index_e == -1:
            string=  self._line[:index_j]
        elif index_j == -1:
            string = self._line[index_e + 1:]
        else:
            string = self._line[index_e + 1: index_j]
        words = string.split()
        for w in words:
            if len(w) != 0:
                return w

    def jump(self):
        """
        Should only be called when command_type() returns C_COMMAND

        :return:
        Returns the jump mneumonic in the current C-command(8 possibilities)
        """
        index = self._line.find(";")
        if index == -1:
            return None
        words = self._line[index + 1:].split()
        for w in words:
            if len(w) != 0:
                return w


class Code:
    """
    Translates Hack assembly language mneumonics to binary code
    """

    def __init__(self):
        self.dest_dict = {}
        self._load_dest()
        self.comp_dict = {}
        self._load_comp()
        self.jump_dict = {}
        self._load_jump()

    def _load_dest(self):
        self.dest_dict[None] = '000'
        self.dest_dict['M'] = '001'
        self.dest_dict['D'] = '010'
        self.dest_dict['MD'] = '011'
        self.dest_dict['A'] = '100'
        self.dest_dict['AM'] = '101'
        self.dest_dict['AD'] = '110'
        self.dest_dict['AMD'] = '111'

    def _load_comp(self):
        self.comp_dict['0'] = '0101010'
        self.comp_dict['1'] = '0111111'
        self.comp_dict['-1'] = '0111010'
        self.comp_dict['D'] = '0001100'
        self.comp_dict['A'] = '0110000'
        self.comp_dict['!D'] = '0001101'
        self.comp_dict['!A'] = '0110011'
        self.comp_dict['-D'] = '0001111'
        self.comp_dict['-A'] = '0110011'
        self.comp_dict['-A'] = '0110011'
        self.comp_dict['D+1'] = '0011111'
        self.comp_dict['A+1'] = '0110111'
        self.comp_dict['D-1'] = '0001110'
        self.comp_dict['A-1'] = '0110010'
        self.comp_dict['D+A'] = '0000010'
        self.comp_dict['D-A'] = '0010011'
        self.comp_dict['A-D'] = '0000111'
        self.comp_dict['D&A'] = '0000000'
        self.comp_dict['D|A'] = '0010101'
        self.comp_dict['M'] = "1110000"
        self.comp_dict['!M'] = "1110001"
        self.comp_dict['-M'] = "1110011"
        self.comp_dict["M+1"] = "1110111"
        self.comp_dict["M-1"] = "1110010"
        self.comp_dict["D+M"] = "1000010"
        self.comp_dict["D-M"] = "1010011"
        self.comp_dict["M-D"] = "1000111"
        self.comp_dict["D&M"] = "1000000"
        self.comp_dict["D|M"] = "1010101"

    def _load_jump(self):
        self.jump_dict[None] = '000'
        self.jump_dict['JGT'] = '001'
        self.jump_dict['JEQ'] = '010'
        self.jump_dict['JGE'] = '011'
        self.jump_dict['JLT'] = '100'
        self.jump_dict['JNE'] = '101'
        self.jump_dict['JLE'] = '110'
        self.jump_dict['JMP'] = '111'

    def dest(self, mneumoic):
        """

        :param mneumoic:
        :return:
        Returns the 3 bit binary code for the destination mneumonic
        """
        return self.dest_dict[mneumoic]

    def comp(self, mneumoic):
        """

        :param mneumoic:
        :return:
        Returns the 7 bit binary code for the comp mneumonic
        """
        return self.comp_dict[mneumoic]

    def jump(self, mneumoic):
        """

        :param mneumoic:
        :return:
        Returns the 3 bit binary code for the jump mneumonic
        """
        return self.jump_dict[mneumoic]


class SymbolTable:
    """
    Keeps a correspondance between symbolic labels and numeric addresses
    """

    def __init__(self):
        """
        Creates new empty symbol table
        """
        self._symbol_table = {}
        self._load_predefined_symbols()

    def add_entry(self, symbol, address):
        """
        Adds the pair(symbol, address) to the symbol table

        :param symbol: symbol from instruction
        :param address: address(int) for the symbol
        :return:
        """
        self._symbol_table[symbol] = address

    def contains(self, symbol):
        """
        Does the symbol table contain the given symbol

        :param symbol: symbol from instruction
        :return:
        True if symbol in symbol table , false otherwise
        """
        return symbol in self._symbol_table

    def get_address(self, symbol):
        """
        :param symbol: symbol from instruction
        :return:
        Returns the address associated with the symbol
        """
        return self._symbol_table[symbol]

    def _load_predefined_symbols(self):
        self._symbol_table['SP'] = 0
        self._symbol_table['LCL'] = 1
        self._symbol_table['ARG'] = 2
        self._symbol_table['THIS'] = 3
        self._symbol_table['THAT'] = 4
        self._symbol_table['SCREEN'] = 16384
        for i in range(0, 16):
            self._symbol_table["R" + str(i)] = i
        self._symbol_table['KBD'] = 24576


class Driver:
    """
    Class to drive program execution

    """

    @staticmethod
    def start(file_name):
        s = SymbolTable()
        p = Parser(file_name)
        c = Code()
        instruction_count = 0
        # first pass - adding program labels to the symbol table
        while True:
            if p.command_type() == Parser.A_COMMAND or p.command_type() == Parser.C_COMMAND:
                instruction_count += 1
            if p.command_type() == Parser.L_COMMAND:
                symbol = p.symbol()
                s.add_entry(symbol, instruction_count)
            if p.has_more_commands():
                p.advance()
            else:
                break

        ram_address_count = 16  # required for variables
        index = file_name.find(".")
        new_file = file_name[0:index] + ".hack"
        file = open(new_file, "w")
        # second pass
        p = Parser(file_name)
        while True:
            if p.command_type() == Parser.A_COMMAND:
                symbol = p.symbol()
                if not symbol.isdigit() and not s.contains(symbol):
                    address = ram_address_count
                    s.add_entry(symbol, address)
                    ram_address_count += 1
                elif s.contains(symbol):
                    address = s.get_address(symbol)
                else:
                    address = symbol
                # now do translation
                out = numpy.binary_repr(int(address), 15)
                file.write("0" + out + "\n")
            if p.command_type() == Parser.C_COMMAND:
                out = c.comp(p.comp()) + c.dest(p.dest()) + c.jump(p.jump())
                file.write("111" + out + "\n")
            if p.has_more_commands():
                p.advance()
            else:
                break


if __name__ == '__main__':
    """
    Entry point of program for execution
    """
    Driver.start("Max.asm")
