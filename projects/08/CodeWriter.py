"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    labels_counter = '1'
    call_counter = '1'
    function_counter = '1'
    return_counter = '1'

    curr_function = ''

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.file_name = ""

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
        filename (str): The name of the VM file.
        """
        self.file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        to_write = ""

        if command == "add":
            to_write += "// Add\n" + \
                        self.take_two_vals() + \
                        "D=D+M\n" + \
                        self.push_result()

        elif command == "sub":
            to_write += "// Sub\n" + \
                        self.take_two_vals() + \
                        "D=D-M\n" + \
                        "D=-D\n" + \
                        self.push_result()

        elif command == "neg":
            to_write += "// Negative\n" + \
                        self.take_val() + \
                        "D=-M\n" + \
                        self.push_result()

        elif command == "eq":
            to_write += "// Equal\n" + \
                        self.take_two_vals() + self.set_bool_by_condition("JEQ")
            CodeWriter.labels_counter = str(int(CodeWriter.labels_counter) + 1)

        elif command == "gt":
            to_write += "// GT\n" + \
                        self.take_val() + \
                        "D=M\n" + \
                        "@R14\n" + \
                        "M=D\n" + \
                        self.take_val() + \
                        "D=M\n" + \
                        "@R13\n" + \
                        "M=D\n" + \
                        self.overflow_check("0", "-1") + \
                        self.set_bool_by_condition("JGT") + \
                        "(END" + CodeWriter.labels_counter + ")\n"

            CodeWriter.labels_counter = str(int(CodeWriter.labels_counter) + 1)

        elif command == "lt":
            to_write += "// LT\n" + \
                        self.take_val() + \
                        "D=M\n" + \
                        "@R14\n" + \
                        "M=D\n" + \
                        self.take_val() + \
                        "D=M\n" + \
                        "@R13\n" + \
                        "M=D\n" + \
                        self.overflow_check("-1", "0") + \
                        self.set_bool_by_condition("JLT") + \
                        "(END" + CodeWriter.labels_counter + ")\n"

            CodeWriter.labels_counter = str(int(CodeWriter.labels_counter) + 1)

        elif command == "and":
            to_write += "// And\n" + \
                        self.take_two_vals() + \
                        "D=D&M\n" + \
                        self.push_result()

        elif command == "or":
            to_write += "// Or\n" + \
                        self.take_two_vals() + \
                        "D=D|M\n" + \
                        self.push_result()

        elif command == "not":
            to_write += "// Not\n" + \
                        self.take_val() + \
                        "D=!M\n" + \
                        self.push_result()

        elif command == "shiftleft":
            to_write += "// Shift left\n" + \
                        self.take_val() + \
                        "D=M\n" + \
                        "D=D<<\n" + \
                        self.push_result()

        elif command == "shiftright":
            to_write += "// Shift right\n" + \
                        self.take_val() + \
                        "D=M\n" + \
                        "D=D>>\n" + \
                        self.push_result()

        self.output_stream.write(to_write)

    def overflow_check(self, if_JLT, if_JGE) -> str:
        return "@XJGE" + CodeWriter.labels_counter + "\n" + \
               "D;JGE\n" + \
               "@R14\n" + \
               "D=M\n" + \
               "@YJGE" + CodeWriter.labels_counter + "\n" + \
               "D;JGE\n" + \
               "@CHECKCOND" + CodeWriter.labels_counter + "\n" + \
               "0;JMP\n" + \
               "(XJGE" + CodeWriter.labels_counter + ")\n" + \
               "    @R14\n" + \
               "    D=M\n" + \
               "    @YJLT" + CodeWriter.labels_counter + "\n" + \
               "    D;JLT\n" + \
               "    @CHECKCOND" + CodeWriter.labels_counter + "\n" + \
               "    0;JMP\n" + \
               "(YJGE" + CodeWriter.labels_counter + ")\n" + \
               "    @SP\n" + \
               "    A=M\n" + \
               "    M=" + if_JLT + "\n" + \
               "    @SP\n" + \
               "    M=M+1\n" + \
               "    @END" + CodeWriter.labels_counter + "\n" + \
               "    0;JMP\n" + \
               "(YJLT" + CodeWriter.labels_counter + ")\n" + \
               "    @SP\n" + \
               "    A=M\n" + \
               "    M=" + if_JGE + "\n" + \
               "    @SP\n" + \
               "    M=M+1\n" + \
               "    @END" + CodeWriter.labels_counter + "\n" + \
               "    0;JMP\n" + \
               "(CHECKCOND" + CodeWriter.labels_counter + ")\n" + \
               "    @R14\n" + \
               "    D=M\n" + \
               "    @R13\n"

    def write_push_pop(self, command: str, segment: str, index: int) -> None:

        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        to_write = "// " + command + " " + segment + " " + str(index) + " \n"

        if segment == "local":
            if command == "C_PUSH":
                to_write += self.first_four_seg_push("LCL", str(index))
            elif command == "C_POP":
                to_write += self.first_four_seg_pop("LCL", str(index))

        elif segment == "argument":
            if command == "C_PUSH":
                to_write += self.first_four_seg_push("ARG", str(index))
            elif command == "C_POP":
                to_write += self.first_four_seg_pop("ARG", str(index))

        elif segment == "this":
            if command == "C_PUSH":
                to_write += self.first_four_seg_push("THIS", str(index))
            elif command == "C_POP":
                to_write += self.first_four_seg_pop("THIS", str(index))

        elif segment == "that":
            if command == "C_PUSH":
                to_write += self.first_four_seg_push("THAT", str(index))
            elif command == "C_POP":
                to_write += self.first_four_seg_pop("THAT", str(index))

        elif segment == "constant":
            if command == "C_PUSH":
                to_write += "@" + str(index) + "\n" + \
                            "D=A\n" + self.push_arg()

            elif command == "C_POP":
                # No pop command in constant
                pass

        elif segment == "static":
            if command == "C_PUSH":
                to_write += "@" + self.file_name + "." + str(index) + "\n" + \
                            "D=M\n" + self.push_arg()
            elif command == "C_POP":
                to_write += self.pop_arg() + \
                            "@" + self.file_name + "." + str(index) + "\n" + \
                            "M=D\n"


        elif segment == "temp":
            if command == "C_PUSH":
                to_write += "@" + str(index) + "\n" + \
                            "D=A\n" + \
                            "@5\n" + \
                            "A=D+A\n" + \
                            "D=M\n" + self.push_arg()
            elif command == "C_POP":
                to_write += "@" + str(index) + "\n" + \
                            "D=A\n" + \
                            "@5\n" + \
                            "D=D+A\n" + \
                            "@R13\n" + \
                            "M=D\n" + self.pop_arg() + \
                            "@R13\n" + \
                            "A=M\n" + \
                            "M=D\n"

        elif segment == "pointer":
            if command == "C_PUSH":
                to_write += "@THIS\n" + \
                            "D=A\n" + \
                            "@" + str(index) + "\n" + \
                            "D=D+A\n" + \
                            "A=D\n"

                to_write += "D=M\n" + self.push_arg()

            elif command == "C_POP":
                to_write += "@THIS\n" + \
                            "D=A\n" + \
                            "@" + str(index) + "\n" + \
                            "D=D+A\n" + \
                            "@R13\n" + \
                            "M=D\n" + \
                            self.pop_arg() + \
                            "@R13\n" + \
                            "A=M\n" + \
                            "M=D\n"

        self.output_stream.write(to_write)

    def take_two_vals(self) -> str:
        return "@SP\n" + \
               "M=M-1\n" + \
               "A=M\n" + \
               "D=M\n" + \
               "@SP\n" + \
               "M=M-1\n" + \
               "A=M\n"

    def take_val(self) -> str:
        return "@SP\n" + \
               "M=M-1\n" + \
               "A=M\n"

    def push_result(self) -> str:
        return "@SP\n" + \
               "A=M\n" + \
               "M=D\n" + \
               "@SP\n" + \
               "M=M+1\n"

    def set_bool_by_condition(self, condition) -> str:
        return "D=D-M\n" + \
               "D=-D\n" + \
               "@SETTRUE" + CodeWriter.labels_counter + "\n" + \
               "D;" + condition + "\n" + \
               "@SP\n" + \
               "A=M\n" + \
               "M=0\n" + \
               "@CONTINUE" + CodeWriter.labels_counter + "\n" + \
               "0;JMP\n" + \
               "(SETTRUE" + CodeWriter.labels_counter + ")\n" + \
               "    @SP\n" + \
               "    A=M\n" + \
               "    M=-1\n" + \
               "    A=M\n" + \
               "(CONTINUE" + CodeWriter.labels_counter + ")\n" + \
               "    @SP\n" + \
               "    M=M+1\n"

    def first_four_seg_push(self, seg, index) -> str:
        # Change segment to segment + index
        output = "@" + seg + "\n" + \
                 "D=M\n" + \
                 "@" + index + "\n" + \
                 "D=D+A\n" + \
                 "@" + seg + "\n" + \
                 "M=D\n"

        # Save segment + index as D
        output += "@" + seg + "\n" + \
                  "A=M\n" + \
                  "D=M\n"

        # Push D to the stack
        output += self.push_arg()

        # Change segment + index to segment
        output += "@" + seg + "\n" + \
                  "D=M\n" + \
                  "@" + index + "\n" + \
                  "D=D-A\n" + \
                  "@" + seg + "\n" + \
                  "M=D\n"

        return output

    def first_four_seg_pop(self, seg, index) -> str:
        # Change segment to segment + index
        output = "@" + seg + "\n" + \
                 "D=M\n" + \
                 "@" + index + "\n" + \
                 "D=D+A\n" + \
                 "@" + seg + "\n" + \
                 "M=D\n"

        # Save as D the last value of the stack
        output += self.pop_arg()

        # Push D to segment + index
        output += "@" + seg + "\n" + \
                  "A=M\n" + \
                  "M=D\n"

        # Change segment + index to segment
        output += "@" + seg + "\n" + \
                  "D=M\n" + \
                  "@" + index + "\n" + \
                  "D=D-A\n" + \
                  "@" + seg + "\n" + \
                  "M=D\n"

        return output

    def push_arg(self) -> str:
        # We assume that D contains the value we want to push to the stack
        return "@SP\n" + \
               "A=M\n" + \
               "M=D\n" + \
               "@SP\n" + \
               "M=M+1\n"

    def pop_arg(self) -> str:
        # At the end of the function, D = last value of the stack
        return "@SP\n" + \
               "M=M-1\n" + \
               "A=M\n" + \
               "D=M\n"

    def close(self) -> None:
        """Closes the output file."""
        self.output_stream.close()

    def write_init(self) -> None:
        """
        Writes the assembly code that effects the
        VM initialization (also called bootstrap
        code). This code should be placed in the
        ROM beginning in address 0x0000.

        :return: None
        """
        to_write = "// init\n" + \
                   "@256\n" + \
                   "D=A\n" + \
                   "@SP\n" + \
                   "M=D\n"
        self.output_stream.write(to_write)
        self.write_call("Sys.init", 0)

    def write_label(self, label: str) -> None:
        """
        Writes the assembly code that is the
        translation of the given label command.

        :param label:
        :return: None
        """
        to_write = "// label " + label + "\n" + \
                   "(" + CodeWriter.curr_function + "$" + label + ")\n"

        self.output_stream.write(to_write)

    def write_goto(self, label: str) -> None:
        """
        Writes the assembly code that is the
        translation of the given goto command.

        :param label:
        :return: None
        """
        to_write = "// Goto " + label + "\n" + \
                   "@" + CodeWriter.curr_function + "$" + label + "\n" + \
                   "0;JMP\n"

        self.output_stream.write(to_write)

    def write_if(self, label: str) -> None:
        """
        Writes the assembly code that is the
        translation of the given if-goto command.

        :param label:
        :return: None
        """

        to_write = "// if-goto " + label + "\n" + \
                   self.pop_arg() + \
                   "@" + CodeWriter.curr_function + "$" + label + "\n" + \
                   "D;JNE\n"

        self.output_stream.write(to_write)

    def write_function(self, function_name: str, num_vars: int) -> None:
        """
        Writes the assembly code that is the
        translation of the given Call command.

        :param function_name:
        :param num_vars:
        :return: None
        """
        to_write = "// Function " + function_name + " " + str(num_vars) + "\n" + \
                   "(" + function_name + ")\n" + \
                   "@" + str(num_vars) + "\n" + \
                   "D=A" + "\n" + \
                   "(PUSHARGS" + CodeWriter.function_counter + ")\n" + \
                   "@ENDFUNCTION" + CodeWriter.function_counter + "\n" + \
                   "D;JLE\n" + \
                   "D=D-1\n" + \
                   "@R13\n" + \
                   "M=D\n" + \
                   "D=0\n" + \
                   self.push_arg() + \
                   "@R13\n" + \
                   "D=M\n" + \
                   "@PUSHARGS" + CodeWriter.function_counter + "\n" + \
                   "D;JGT\n" + \
                   "(ENDFUNCTION" + CodeWriter.function_counter + ")\n"

        CodeWriter.function_counter = str(int(CodeWriter.function_counter) + 1)

        # CodeWriter.curr_function.append(function_name)

        CodeWriter.curr_function = function_name

        self.output_stream.write(to_write)

    def write_call(self, function_name: str, num_vars: int) -> None:
        """
        Writes the assembly code that is the
        translation of the given Return command.

        :param function_name:
        :param num_vars:
        :return: None
        """

        to_write = "// Call " + function_name + " " + str(num_vars) + "\n" + \
                   "@RETURNTO" + CodeWriter.call_counter + "\n" + \
                   "D=A\n" + \
                   self.push_arg() + \
                   "@LCL\n" + \
                   "D=M\n" + \
                   self.push_arg() + \
                   "@ARG\n" + \
                   "D=M\n" + \
                   self.push_arg() + \
                   "@THIS\n" + \
                   "D=M\n" + \
                   self.push_arg() + \
                   "@THAT\n" + \
                   "D=M\n" + \
                   self.push_arg() + \
                   "@SP\n" + \
                   "D=M\n" + \
                   "@5\n" + \
                   "D=D-A\n" + \
                   "@" + str(num_vars) + "\n" \
                   "D=D-A\n" + \
                   "@ARG\n" + \
                   "M=D\n" + \
                   "@SP\n" + \
                   "D=M\n" + \
                   "@LCL\n" + \
                   "M=D\n" + \
                   "@" + function_name + "\n" + \
                   "0;JMP\n" + \
                   "(RETURNTO" + CodeWriter.call_counter + ")\n"

        CodeWriter.call_counter = str(int(CodeWriter.call_counter) + 1)

        self.output_stream.write(to_write)

    def write_return(self) -> None:
        """
        Writes the assembly code that is the trans. of
        the given Function command.

        :return: None
        """

        to_write = "// Return\n" + \
                   "@LCL\n" + \
                   "D=M\n" + \
                   "@ENDFRAME" + CodeWriter.return_counter + "\n" + \
                   "M=D\n" + \
                   "@5\n" + \
                   "D=D-A\n" + \
                   "A=D\n" + \
                   "D=M\n" + \
                   "@RETADDR" + CodeWriter.return_counter + "\n" + \
                   "M=D\n" + \
                   self.pop_arg() + \
                   "@ARG\n" + \
                   "A=M\n" + \
                   "M=D\n" + \
                   "@ARG\n" + \
                   "D=M\n" + \
                   "@SP\n" + \
                   "M=D+1\n" + \
                   "@ENDFRAME" + CodeWriter.return_counter + "\n" + \
                   "D=M\n" + \
                   "D=D-1\n" + \
                   "A=D\n" + \
                   "D=M\n" + \
                   "@THAT\n" + \
                   "M=D\n" + \
                   "@ENDFRAME" + CodeWriter.return_counter + "\n" + \
                   "D=M\n" + \
                   "@2\n" + \
                   "D=D-A\n" + \
                   "A=D\n" + \
                   "D=M\n" + \
                   "@THIS\n" + \
                   "M=D\n" + \
                   "@ENDFRAME" + CodeWriter.return_counter + "\n" + \
                   "D=M\n" + \
                   "@3\n" + \
                   "D=D-A\n" + \
                   "A=D\n" + \
                   "D=M\n" + \
                   "@ARG\n" + \
                   "M=D\n" + \
                   "@ENDFRAME" + CodeWriter.return_counter + "\n" + \
                   "D=M\n" + \
                   "@4\n" + \
                   "D=D-A\n" + \
                   "A=D\n" + \
                   "D=M\n" + \
                   "@LCL\n" + \
                   "M=D\n" + \
                   "@RETADDR" + CodeWriter.return_counter + "\n" + \
                   "A=M\n" + \
                   "0;JMP\n"

        CodeWriter.return_counter = str(int(CodeWriter.return_counter) + 1)

        self.output_stream.write(to_write)
