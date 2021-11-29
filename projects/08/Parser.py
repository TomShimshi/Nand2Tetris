"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

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
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        self.curr_index += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        curr_line = self.input_lines[self.curr_index].split("//")[0].replace(" ", "")\
            .replace("/t","")
        if curr_line == "":
            return ""
        if "push" in curr_line:
            return "C_PUSH"
        elif "pop" in curr_line:
            return "C_POP"
        elif "label" in curr_line:
            return "C_LABEL"
        elif "if" in curr_line:
            return "C_IF"
        elif "goto" in curr_line:
            return "C_GOTO"
        elif "function" in curr_line:
            return "C_FUNCTION"
        elif "return" in curr_line:
            return "C_RETURN"
        elif "call" in curr_line:
            return "C_CALL"
        else:
            return "C_ARITHMETIC"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        # curr_line = self.input_lines[self.curr_index].split("//")[0]
        # if curr_line == "":
        #     return ""
        if self.command_type() == "C_ARITHMETIC":
            return self.input_lines[self.curr_index].split("//")[0].split(" ")[0].replace("\t","")
        return self.input_lines[self.curr_index].split("//")[0].split(" ")[1].replace("\t","")

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.input_lines[self.curr_index].split("//")[0].split(" ")[2].replace("\t",""))
