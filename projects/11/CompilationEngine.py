"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream: "VMWriter",
                 symbol_table: "SymbolTable") -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.jack_tokenizer = input_stream
        self.vm_writer = output_stream
        self.symbol_table = symbol_table

        self.class_name = ""
        self.subroutine_name = ""

        self.if_counter = 0
        self.while_counter = 0

    def compile_class(self) -> None:
        """Compiles a complete class."""

        # keyword class
        self.jack_tokenizer.advance()
        self.class_name = self.jack_tokenizer.identifier()  # class name
        self.jack_tokenizer.advance() # {
        self.jack_tokenizer.advance()

        # Compile all the class variables #
        if self.jack_tokenizer.token_type() == "KEYWORD":
            while self.jack_tokenizer.keyword() in ["field", "static"]:
                self.compile_variable()

        # Compile all the class subroutines #
        if self.jack_tokenizer.token_type() == "KEYWORD":
            while self.jack_tokenizer.keyword() in ["method", "constructor", "function"]:
                self.symbol_table.start_subroutine()
                self.compile_subroutine()

        return

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        subroutine_type = self.jack_tokenizer.keyword()

        self.jack_tokenizer.advance()
        type_return_value = self.compile_type()
        self.jack_tokenizer.advance()
        subroutine_name = self.jack_tokenizer.identifier()

        self.jack_tokenizer.advance()  # (
        self.jack_tokenizer.advance()

        if subroutine_type == "method":
            self.symbol_table.define("this", self.class_name, "argument")


        self.compile_parameter_list()

        self.jack_tokenizer.advance()

        # Compile Subroutine Body

        self.jack_tokenizer.advance()


        if self.jack_tokenizer.token_type() == "KEYWORD":
            while self.jack_tokenizer.keyword() == "var":
                self.compile_variable()


        self.vm_writer.write_function(self.class_name + "." + subroutine_name,
                                      self.symbol_table.var_count("var"))

        if subroutine_type == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)
        elif subroutine_type == "constructor":
            self.vm_writer.write_push("constant", self.symbol_table.var_count("field"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)

        self.compile_statements()

        self.jack_tokenizer.advance()
        return

    def compile_parameter_list(self) -> None:
        """
        Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        :return:
        """
        if self.jack_tokenizer.token_type() == "SYMBOL":  # no parameters, return 0
            return

        arg_type = self.compile_type()
        self.jack_tokenizer.advance()
        arg_name = self.jack_tokenizer.identifier()
        self.symbol_table.define(arg_name, arg_type, "argument")


        self.jack_tokenizer.advance()
        while self.jack_tokenizer.symbol() == ',':
            self.jack_tokenizer.advance()
            arg_type = self.compile_type()
            self.jack_tokenizer.advance()
            arg_name = self.jack_tokenizer.identifier()
            self.symbol_table.define(arg_name, arg_type, "argument")
            self.jack_tokenizer.advance()

        return

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.jack_tokenizer.token_type() == "KEYWORD":
            keyword = self.jack_tokenizer.keyword()
            if keyword == 'let':
                self.compile_let()
            elif keyword == 'if':
                self.compile_if()
            elif keyword == 'while':
                self.compile_while()
            elif keyword == 'do':
                self.compile_do()
            elif keyword == 'return':
                self.compile_return()
        return

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.jack_tokenizer.advance()
        self.compile_subroutine_call()
        self.vm_writer.write_pop("temp", 0)
        self.jack_tokenizer.advance()

    def compile_let(self) -> None:
        """Compiles a let statement."""

        self.jack_tokenizer.advance()  # let
        identifier = self.jack_tokenizer.identifier()
        self.jack_tokenizer.advance()  # identifier

        if self.jack_tokenizer.token_type() == "SYMBOL":
            if self.jack_tokenizer.symbol() == '[':
                self.jack_tokenizer.advance()  # [
                self.compile_expression()
                segment = self.convert_kind_to_segment(self.symbol_table.kind_of(identifier))
                index = self.symbol_table.index_of(identifier)
                self.vm_writer.write_push(segment, index)
                self.vm_writer.write_arithmetic("add")
                self.jack_tokenizer.advance()  # ]

                if self.jack_tokenizer.symbol() == '=':
                    self.jack_tokenizer.advance()  # =
                    self.compile_expression()

                    self.vm_writer.write_pop('temp', 0)
                    self.vm_writer.write_pop('pointer', 1)
                    self.vm_writer.write_push('temp', 0)
                    self.vm_writer.write_pop('that', 0)

                    self.jack_tokenizer.advance()  # ;


            elif self.jack_tokenizer.symbol() == '=':
                self.jack_tokenizer.advance()  # =
                self.compile_expression()
                segment = self.convert_kind_to_segment(self.symbol_table.kind_of(identifier))
                index = self.symbol_table.index_of(identifier)
                self.vm_writer.write_pop(segment, index)

                self.jack_tokenizer.advance()  # ;

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.jack_tokenizer.advance()  # while
        while_index = self.while_counter
        self.while_counter += 1
        self.vm_writer.write_label("WHILE_TRUE" + str(while_index))

        if self.jack_tokenizer.token_type() == "SYMBOL":
            self.jack_tokenizer.advance()  # (
            self.compile_expression()
            self.jack_tokenizer.advance()  # )

            self.vm_writer.write_arithmetic("not")
            self.vm_writer.write_if("WHILE_FALSE" + str(while_index))

        if self.jack_tokenizer.token_type() == "SYMBOL":
            self.jack_tokenizer.advance()  # {
            self.compile_statements()
            self.jack_tokenizer.advance()  # }
            self.vm_writer.write_goto("WHILE_TRUE" + str(while_index))

        self.vm_writer.write_label("WHILE_FALSE" + str(while_index))



    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.jack_tokenizer.advance()  # return

        if not (self.jack_tokenizer.token_type() == 'SYMBOL' and self.jack_tokenizer.symbol()
                == ';'):
            self.compile_expression()

        else:
            self.vm_writer.write_push("constant", 0)

        self.vm_writer.write_return()

        self.jack_tokenizer.advance()  # ;

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""

        self.jack_tokenizer.advance()
        if_index = self.if_counter
        self.if_counter += 1

        # expressions
        if self.jack_tokenizer.token_type() == "SYMBOL":
            self.jack_tokenizer.advance()  # (
            self.compile_expression()
            self.jack_tokenizer.advance()  # )
            self.vm_writer.write_arithmetic("not")

        # statements
        if self.jack_tokenizer.token_type() == "SYMBOL":
            self.jack_tokenizer.advance()  # {
            self.vm_writer.write_if("IF_FALSE" + str(if_index))
            self.compile_statements()
            self.jack_tokenizer.advance()  # }
            self.vm_writer.write_goto("IF_TRUE" + str(if_index))

        self.vm_writer.write_label("IF_FALSE" + str(if_index))

        # else
        if self.jack_tokenizer.token_type() == "KEYWORD" and \
                self.jack_tokenizer.keyword() == 'else':
            self.jack_tokenizer.advance()
            self.jack_tokenizer.advance()  # {
            self.compile_statements()
            self.jack_tokenizer.advance()  # }

        self.vm_writer.write_label("IF_TRUE" + str(if_index))

    def compile_subroutine_call(self, identifier=False) -> None:
        """
        Compile a call to a subroutine
        :param identifier: identifier from term if relevant
        :return: None
        """
        is_method = False
        args_num = 0

        # Check if we got already identifier from term
        if identifier:
            subroutine_name = identifier
        else:
            subroutine_name = self.jack_tokenizer.identifier()
            self.jack_tokenizer.advance()

        symbol_type = self.symbol_table.type_of(subroutine_name)

        if symbol_type:  # if the subroutine_name is var

            kind = self.convert_kind_to_segment(self.symbol_table.kind_of(subroutine_name))
            index = self.symbol_table.index_of(subroutine_name)
            subroutine_name = symbol_type
            is_method = True

        if self.jack_tokenizer.token_type() == 'SYMBOL' and self.jack_tokenizer.symbol() == ".":
            # if entered- there is a className or varName

            self.jack_tokenizer.advance()
            subroutine_name += "." + self.jack_tokenizer.identifier()

            self.jack_tokenizer.advance()

        else:
            kind = "pointer"
            index = 0
            subroutine_name = self.class_name + "." + subroutine_name
            is_method = True


        self.jack_tokenizer.advance()

        if is_method:
            self.vm_writer.write_push(kind, index)
            args_num += 1

        args_num += self.compile_expression_list()

        self.vm_writer.write_call(subroutine_name, args_num)

        self.jack_tokenizer.advance()

    def compile_term(self, identifier=False) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        token_type = self.jack_tokenizer.token_type()
        if token_type == 'STRING_CONST':
            str_val = self.jack_tokenizer.string_val()
            length = len(str_val)
            self.vm_writer.write_push("constant", length)
            self.vm_writer.write_call("String.new", 1)
            for char in str_val:
                ascii_code_char = ord(char)
                self.vm_writer.write_push("constant", ascii_code_char)
                self.vm_writer.write_call("String.appendChar", 2)

            self.jack_tokenizer.advance()

        elif token_type == 'INT_CONST':
            self.vm_writer.write_push("constant", self.jack_tokenizer.int_val())
            self.jack_tokenizer.advance()

        elif token_type == 'KEYWORD':
            keyword = self.jack_tokenizer.keyword()
            if keyword == "this":
                self.vm_writer.write_push("pointer", 0)
            else:
                self.vm_writer.write_push("constant", 0)
                if keyword == "true":
                    self.vm_writer.write_arithmetic("not")

            self.jack_tokenizer.advance()

        elif token_type == 'SYMBOL':
            symbol = self.jack_tokenizer.symbol()
            if symbol == '-':
                self.jack_tokenizer.advance()
                self.compile_term()
                self.vm_writer.write_arithmetic("neg")

            elif symbol == "~":
                self.jack_tokenizer.advance()
                self.compile_term()
                self.vm_writer.write_arithmetic("not")

            if symbol == "(":
                self.jack_tokenizer.advance()
                self.compile_expression()
                self.jack_tokenizer.advance()

        else:
            identifier = self.jack_tokenizer.identifier()
            self.jack_tokenizer.advance()
            next_token_type = self.jack_tokenizer.token_type()
            if next_token_type == "SYMBOL":
                next_symbol = self.jack_tokenizer.symbol()
                if next_symbol == "[":
                    segment = self.convert_kind_to_segment(self.symbol_table.kind_of(identifier))
                    self.vm_writer.write_push(segment, self.symbol_table.index_of(identifier))
                    self.jack_tokenizer.advance()
                    self.compile_expression()
                    self.vm_writer.write_arithmetic("add")
                    self.vm_writer.write_pop("pointer", 1)
                    self.vm_writer.write_push("that", 0)
                    self.jack_tokenizer.advance()
                elif next_symbol == "(" or next_symbol == ".":
                    self.compile_subroutine_call(identifier)
                else:  # varName
                    segment = self.convert_kind_to_segment(self.symbol_table.kind_of(identifier))
                    self.vm_writer.write_push(segment, self.symbol_table.index_of(identifier))
            else:
                segment = self.convert_kind_to_segment(self.symbol_table.kind_of(identifier))
                self.vm_writer.write_push(segment, self.symbol_table.index_of(identifier))

        return

    def compile_expression(self) -> None:
        """Compiles an expression."""

        self.compile_term()
        shifts_lst = ["<<", ">>"]
        shift_to_compile = []

        while self.jack_tokenizer.token_type() == "SYMBOL" and self.jack_tokenizer.symbol() in {
            "+", "-", "*", "/", "&amp;", "|", "&gt;", "&lt;", "=", "<<", ">>"}:
            symbol = self.jack_tokenizer.symbol()
            if symbol in shifts_lst:
                shift_to_compile.append(symbol)
            self.jack_tokenizer.advance()


            while self.jack_tokenizer.token_type() == "SYMBOL" and self.jack_tokenizer.symbol() in \
                    shifts_lst:
                shift_to_compile.append(self.jack_tokenizer.symbol())
                self.jack_tokenizer.advance()


            self.compile_term()
            if symbol == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            elif symbol == "/":
                self.vm_writer.write_call("Math.divide", 2)
            elif shift_to_compile:
                reversed(shift_to_compile)
                for shift in reversed(shift_to_compile):
                    self.vm_writer.write_arithmetic(self.convert_symbol_to_op(shift))
            else:
                self.vm_writer.write_arithmetic(self.convert_symbol_to_op(symbol))

    def compile_expression_list(self) -> int:
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        :return: Num of arguments: int
        """
        args_num = 0
        if self.jack_tokenizer.token_type() == "SYMBOL" and self.jack_tokenizer.symbol() == ")":
            return args_num

        self.compile_expression()
        args_num += 1

        while self.jack_tokenizer.token_type() == "SYMBOL" and self.jack_tokenizer.symbol() == ",":
            self.jack_tokenizer.advance()
            self.compile_expression()
            args_num += 1

        return args_num

    def compile_type(self) -> str:
        """
        Choose between identifier or keyword
        :return: Type of the token: str
        """
        if self.jack_tokenizer.token_type() == 'IDENTIFIER':
            return self.jack_tokenizer.identifier()
        return self.jack_tokenizer.keyword()

    def compile_variable(self) -> int:
        """
        Compile all types of variables- field, static and var
        :return: Number of vars declared inside the subroutine- int
        """
        token_kind = self.jack_tokenizer.keyword()
        self.jack_tokenizer.advance()
        token_type = self.compile_type()
        self.jack_tokenizer.advance()
        token_name = self.jack_tokenizer.identifier()

        self.add_variable(token_name, token_type, token_kind)
        self.jack_tokenizer.advance()
        while self.jack_tokenizer.symbol() == ',':
            self.jack_tokenizer.advance()
            token_name = self.jack_tokenizer.identifier()
            self.add_variable(token_name, token_type, token_kind)

            self.jack_tokenizer.advance()  # ; / ,

        self.jack_tokenizer.advance()
        return

    def add_variable(self, token_name, token_type, token_kind) -> None:
        """
        Add variable to symbol table and to memory
        :param token_name: str
        :param token_type: str
        :param token_kind: str
        :return: None
        """
        # add variable to dict
        self.symbol_table.define(token_name, token_type, token_kind)


    def convert_kind_to_segment(self, kind: str) -> str:
        """
        Convert kind of a token to segment
        :param kind: kind of a token: str
        :return: segment: str
        """
        if kind == "field":
            return "this"
        elif kind == "var":
            return "local"

        return kind

    def convert_symbol_to_op(self, symbol: str) -> str:
        """
        Convert symbol of a token to operator
        :param symbol: symbol of a token: str
        :return: op: str
        """
        if symbol == "+":
            return "add"
        elif symbol == "-":
            return "sub"
        elif symbol == "&amp;":
            return "and"
        elif symbol == "|":
            return "or"
        elif symbol == "&gt;":
            return "gt"
        elif symbol == "&lt;":
            return "lt"
        elif symbol == "<<":
            return "shiftleft"
        elif symbol == ">>":
            return "shiftright"
        else:
            return "eq"
