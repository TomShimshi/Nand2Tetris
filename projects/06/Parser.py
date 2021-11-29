"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads and assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    # file_length = 0
    # input_lines = []

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        self.file_length = len(self.input_lines)
        self.curr_index = 0

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.curr_index != self.file_length

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        self.curr_index += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        curr_line = self.input_lines[self.curr_index].split("//")[0].replace(" ", "").replace("\t",
                                                                                              "")
        if curr_line == "":
            return ""
        elif curr_line[0] == "@":
            return "A_COMMAND"
        elif curr_line[0] == "(":
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == "A_COMMAND":
            return self.input_lines[self.curr_index].split("@")[1].split("//")[0].replace(" ","").\
                replace("\t", "")
        elif self.command_type() == "L_COMMAND":
            return self.input_lines[self.curr_index].split("(")[1].split(")")[0].replace(" ","").\
                replace("\t", "")

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        temp = self.input_lines[self.curr_index].split("//")[0].replace(" ", "").replace("\t", "")
        if "=" in temp:
            return temp.split("=")[0]
        return ""

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        temp = self.input_lines[self.curr_index].split("//")[0].replace(" ", "").replace("\t", "")
        if "=" in temp:
            return temp.split("=")[1]
        return temp.split(';')[0]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        temp = self.input_lines[self.curr_index].split("//")[0].replace(" ", "").replace("\t", "")
        if ";" in temp:
            return temp.split(";")[1]
        return ""
