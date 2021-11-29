"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    symbol_table = SymbolTable()
    first_loop_parser = Parser(input_file)

    code = Code()
    line_index = 0
    memory_index = 16

    while first_loop_parser.has_more_commands():
        curr_command_type = first_loop_parser.command_type()
        if curr_command_type == "A_COMMAND":
            line_index += 1

        elif curr_command_type == "L_COMMAND":
            curr_symbol = first_loop_parser.symbol()
            if not (symbol_table.contains(curr_symbol)):
                symbol_table.add_entry(curr_symbol, line_index)

        elif curr_command_type=="C_COMMAND":
            line_index += 1

        first_loop_parser.advance()

    input_file.seek(0)

    second_loop_parser = Parser(input_file)
    while second_loop_parser.has_more_commands():
        curr_command_type = second_loop_parser.command_type()
        if curr_command_type == "A_COMMAND":
            symbol_val = second_loop_parser.symbol()
            if not(symbol_val.isdigit()):
                if not (symbol_table.contains(symbol_val)):
                    symbol_table.add_entry(symbol_val, memory_index)
                    memory_index += 1
                symbol_val = symbol_table.get_address(symbol_val)

            symbol_bin = bin(int(symbol_val)).split("b")[1].zfill(16)

            output_file.write(symbol_bin)
            output_file.write("\n")

        elif curr_command_type == "C_COMMAND":
            val_dest = second_loop_parser.dest()
            val_comp = second_loop_parser.comp()
            val_jump = second_loop_parser.jump()

            bin_dest = code.dest(val_dest)
            bin_comp = code.comp(val_comp)
            bin_jump = code.jump(val_jump)

            initial_bits = "111"
            if ">>" in val_comp or "<<" in val_comp:
                initial_bits = "101"


            symbol_bin = initial_bits + bin_comp + bin_dest + bin_jump
            output_file.write(symbol_bin)
            output_file.write("\n")

        second_loop_parser.advance()


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)

