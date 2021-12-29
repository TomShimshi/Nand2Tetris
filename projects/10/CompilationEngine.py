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

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.jack_tokenizer = input_stream
        self.output_stream = output_stream

    def compile_class(self) -> None:
        """Compiles a complete class."""

        self.output_stream.write("<keyword> {0} </keyword>\n".format(self.jack_tokenizer.keyword()))
        self.jack_tokenizer.advance()
        self.output_stream.write("<identifier> {0} </identifier>\n".format(
            self.jack_tokenizer.identifier()))
        self.jack_tokenizer.advance()
        self.output_stream.write("<symbol> {0} </symbol>\n".format(self.jack_tokenizer.symbol()))
        self.jack_tokenizer.advance()

        ### Compile all the class variables ###
        if self.jack_tokenizer.token_type() == "KEYWORD":
            while self.jack_tokenizer.keyword() in ["static", "field"]:
                self.compile_class_var_dec()

        ### Compile all the class subtoutines ###
        if self.jack_tokenizer.token_type() == "KEYWORD":
            while self.jack_tokenizer.keyword() in ["method", "constructor", "function"]:
                self.compile_subroutine()

        # self.jack_tokenizer.advance()
        self.output_stream.write("<symbol> {0} </symbol>\n".format(self.jack_tokenizer.symbol()))

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output_stream.write("<classVarDec>\n")
        self.compile_variable()
        self.output_stream.write("</classVarDec>\n")

        return

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""

        self.output_stream.write("<subroutineDec>\n")

        self.output_stream.write(
            "<keyword> {0} </keyword>\n".format(self.jack_tokenizer.keyword()))
        self.jack_tokenizer.advance()
        self.compile_type()
        self.jack_tokenizer.advance()
        self.output_stream.write("<identifier> {0} </identifier>\n".format(
            self.jack_tokenizer.identifier()))
        self.jack_tokenizer.advance()
        self.output_stream.write("<symbol> {0} </symbol>\n".format(
            self.jack_tokenizer.symbol()))  # (
        self.jack_tokenizer.advance()
        self.compile_parameter_list()

        self.output_stream.write("<symbol> {0} </symbol>\n".format(
            self.jack_tokenizer.symbol()))  # )

        self.jack_tokenizer.advance()

        # Compile Subroutine Body
        self.output_stream.write("<subroutineBody>\n")

        self.output_stream.write("<symbol> {0} </symbol>\n".format(
            self.jack_tokenizer.symbol()))  # {

        self.jack_tokenizer.advance()

        if self.jack_tokenizer.token_type() == "KEYWORD":
            while self.jack_tokenizer.keyword() == "var":
                self.compile_var_dec()

        self.compile_statements()

        self.output_stream.write("<symbol> {0} </symbol>\n".format(
            self.jack_tokenizer.symbol()))  # }

        self.output_stream.write("</subroutineBody>\n")

        self.jack_tokenizer.advance()

        self.output_stream.write("</subroutineDec>\n")

        return

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output_stream.write("<parameterList>\n")
        if self.jack_tokenizer.token_type() == "SYMBOL":
            self.output_stream.write("</parameterList>\n")
            return

        self.compile_type()
        self.jack_tokenizer.advance()
        self.output_stream.write("<identifier> {0} </identifier>\n".format(
            self.jack_tokenizer.identifier()))
        self.jack_tokenizer.advance()
        while self.jack_tokenizer.symbol() == ',':
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))
            self.jack_tokenizer.advance()
            self.compile_type()
            self.jack_tokenizer.advance()
            self.output_stream.write("<identifier> {0} </identifier>\n".format(
                self.jack_tokenizer.identifier()))
            self.jack_tokenizer.advance()

        self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_stream.write("<varDec>\n")
        self.compile_variable()
        self.output_stream.write("</varDec>\n")

        return

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output_stream.write("<statements>\n")
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

        self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_stream.write("<doStatement>\n")
        self.output_stream.write("<keyword> {0} </keyword>\n".format(
            self.jack_tokenizer.keyword()))  # do

        self.jack_tokenizer.advance()

        ### Subroutine call ###
        self.compile_subroutine_call()
        ### End of Subroutine call ###
        self.output_stream.write("<symbol> {0} </symbol>\n".format(
            self.jack_tokenizer.symbol()))  # ;
        self.jack_tokenizer.advance()
        self.output_stream.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_stream.write("<letStatement>\n")
        self.output_stream.write("<keyword> {0} </keyword>\n".format(
            self.jack_tokenizer.keyword()))  # let

        self.jack_tokenizer.advance()
        self.output_stream.write("<identifier> {0} </identifier>\n".format(
            self.jack_tokenizer.identifier()))
        self.jack_tokenizer.advance()

        if self.jack_tokenizer.token_type() == "SYMBOL":
            if self.jack_tokenizer.symbol() == '[':
                self.output_stream.write("<symbol> [ </symbol>\n")
                self.jack_tokenizer.advance()
                self.compile_expression()
                self.output_stream.write("<symbol> {0} </symbol>\n".format(
                    self.jack_tokenizer.symbol()))  # ]
                self.jack_tokenizer.advance()
            if self.jack_tokenizer.symbol() == '=':
                self.output_stream.write("<symbol> = </symbol>\n")
                self.jack_tokenizer.advance()
                self.compile_expression()
                self.output_stream.write("<symbol> {0} </symbol>\n".format(
                    self.jack_tokenizer.symbol()))  # ;
                self.jack_tokenizer.advance()

        self.output_stream.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_stream.write("<whileStatement>\n")
        self.output_stream.write("<keyword> {0} </keyword>\n".format(
            self.jack_tokenizer.keyword()))  # while
        self.jack_tokenizer.advance()

        if self.jack_tokenizer.token_type() == "SYMBOL":
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # (
            self.jack_tokenizer.advance()
            self.compile_expression()
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # )
            self.jack_tokenizer.advance()

        if self.jack_tokenizer.token_type() == "SYMBOL":
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # {
            self.jack_tokenizer.advance()
            self.compile_statements()
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # }
            self.jack_tokenizer.advance()

        self.output_stream.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_stream.write("<returnStatement>\n")
        self.output_stream.write("<keyword> {0} </keyword>\n".format(
            self.jack_tokenizer.keyword()))  # return
        self.jack_tokenizer.advance()
        if not (self.jack_tokenizer.token_type() == 'SYMBOL' and self.jack_tokenizer.symbol()
                == ';'):
            self.compile_expression()
        self.output_stream.write("<symbol> {0} </symbol>\n".format(
            self.jack_tokenizer.symbol()))  # ;
        self.jack_tokenizer.advance()

        self.output_stream.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output_stream.write("<ifStatement>\n")
        self.output_stream.write("<keyword> {0} </keyword>\n".format(
            self.jack_tokenizer.keyword()))  # if
        self.jack_tokenizer.advance()

        ### expressions ###
        if self.jack_tokenizer.token_type() == "SYMBOL":
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # (
            self.jack_tokenizer.advance()
            self.compile_expression()
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # )
            self.jack_tokenizer.advance()

        ### statements ###
        if self.jack_tokenizer.token_type() == "SYMBOL":
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # {
            self.jack_tokenizer.advance()
            self.compile_statements()
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # }
            self.jack_tokenizer.advance()

        ### else ###
        if self.jack_tokenizer.token_type() == "KEYWORD" and \
                self.jack_tokenizer.keyword() == 'else':
            self.output_stream.write("<keyword> {0} </keyword>\n".format(
                self.jack_tokenizer.keyword()))  # else
            self.jack_tokenizer.advance()
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # {
            self.jack_tokenizer.advance()
            self.compile_statements()
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # }
            self.jack_tokenizer.advance()

        self.output_stream.write("</ifStatement>\n")

    def compile_subroutine_call(self, identifier=False) -> None:
        """
        Compile a call to a subroutine
        :param identifier: identifier from term if relevant
        :return: None
        """
        # Check if we got already identifier from term
        if identifier:
            self.output_stream.write("<identifier> {0} </identifier>\n".format(identifier))
        else:
            self.output_stream.write("<identifier> {0} </identifier>\n".format(
                self.jack_tokenizer.identifier()))
            self.jack_tokenizer.advance()

        if self.jack_tokenizer.token_type() == 'SYMBOL' and self.jack_tokenizer.symbol() == ".":
            # if entered- there is a className or varName
            self.output_stream.write(
                "<symbol> {0} </symbol>\n".format(self.jack_tokenizer.symbol()))
            self.jack_tokenizer.advance()

            self.output_stream.write("<identifier> {0} </identifier>\n".format(
                self.jack_tokenizer.identifier()))  # subroutineName
            self.jack_tokenizer.advance()

        self.output_stream.write("<symbol> {0} </symbol>\n".format(
            self.jack_tokenizer.symbol()))  # (
        self.jack_tokenizer.advance()
        self.compile_expression_list()
        self.output_stream.write("<symbol> {0} </symbol>\n".format(
            self.jack_tokenizer.symbol()))  # )
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
        self.output_stream.write("<term>\n")
        token_type = self.jack_tokenizer.token_type()
        if token_type == 'STRING_CONST':
            self.output_stream.write("<stringConstant> {0} </stringConstant>\n".format(
                self.jack_tokenizer.string_val()))
            self.jack_tokenizer.advance()

        elif token_type == 'INT_CONST':
            self.output_stream.write("<integerConstant> {0} </integerConstant>\n".format(
                self.jack_tokenizer.int_val()))
            self.jack_tokenizer.advance()

        elif token_type == 'KEYWORD':
            self.output_stream.write("<keyword> {0} </keyword>\n".format(
                self.jack_tokenizer.keyword()))
            self.jack_tokenizer.advance()

        elif token_type == 'SYMBOL':
            symbol = self.jack_tokenizer.symbol()
            if symbol in {'-', "~", "#", "^"}:
                self.output_stream.write("<symbol> {0} </symbol>\n".format(symbol))
                self.jack_tokenizer.advance()
                self.compile_term()
            if symbol == "(":
                self.output_stream.write("<symbol> {0} </symbol>\n".format(symbol))
                self.jack_tokenizer.advance()
                self.compile_expression()
                self.output_stream.write("<symbol> {0} </symbol>\n".format(
                    self.jack_tokenizer.symbol()))
                self.jack_tokenizer.advance()

        else:
            identifier = self.jack_tokenizer.identifier()
            self.jack_tokenizer.advance()
            next_token_type = self.jack_tokenizer.token_type()
            if next_token_type == "SYMBOL":
                next_symbol = self.jack_tokenizer.symbol()
                if next_symbol == "[":
                    self.output_stream.write("<identifier> {0} </identifier>\n".format(identifier))
                    self.output_stream.write("<symbol> [ </symbol>\n")
                    self.jack_tokenizer.advance()
                    self.compile_expression()
                    self.output_stream.write("<symbol> ] </symbol>\n")
                    self.jack_tokenizer.advance()
                elif next_symbol == "(" or next_symbol == ".":
                    self.compile_subroutine_call(identifier)
                else:  # varName
                    self.output_stream.write("<identifier> {0} </identifier>\n".format(identifier))
            else:
                self.output_stream.write("<identifier> {0} </identifier>\n".format(identifier))

        self.output_stream.write("</term>\n")

        return

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output_stream.write("<expression>\n")
        self.compile_term()
        while self.jack_tokenizer.token_type() == "SYMBOL" and self.jack_tokenizer.symbol() in {
            "+", "-", "*", "/", "&amp;", "|", "&gt;", "&lt;", "="}:
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))
            self.jack_tokenizer.advance()
            self.compile_term()

        self.output_stream.write("</expression>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_stream.write("<expressionList>\n")
        if self.jack_tokenizer.token_type() == "SYMBOL" and self.jack_tokenizer.symbol() == ")":
            self.output_stream.write("</expressionList>\n")
            return
        self.compile_expression()
        while self.jack_tokenizer.token_type() == "SYMBOL" and self.jack_tokenizer.symbol() == ",":
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # ,
            self.jack_tokenizer.advance()
            self.compile_expression()

        self.output_stream.write("</expressionList>\n")

    def compile_type(self) -> None:
        """
        Choose between identifier or keyword
        :return: None
        """
        if self.jack_tokenizer.token_type() == 'IDENTIFIER':
            self.output_stream.write("<identifier> {0} </identifier>\n".format(
                self.jack_tokenizer.identifier()))
        else:
            self.output_stream.write("<keyword> {0} </keyword>\n".format(
                self.jack_tokenizer.keyword()))

    def compile_variable(self) -> None:
        """
        Compile all types of vaiables- field, static and var
        :return: None
        """
        self.output_stream.write(
            "<keyword> {0} </keyword>\n".format(self.jack_tokenizer.keyword()))
        self.jack_tokenizer.advance()
        self.compile_type()
        self.jack_tokenizer.advance()
        self.output_stream.write("<identifier> {0} </identifier>\n".format(
            self.jack_tokenizer.identifier()))
        self.jack_tokenizer.advance()
        while self.jack_tokenizer.symbol() == ',':
            self.output_stream.write("<symbol> {0} </symbol>\n".format(
                self.jack_tokenizer.symbol()))  # ,
            self.jack_tokenizer.advance()
            self.output_stream.write("<identifier> {0} </identifier>\n".format(
                self.jack_tokenizer.identifier()))
            self.jack_tokenizer.advance()

        self.output_stream.write("<symbol> {0} </symbol>\n".format(
            self.jack_tokenizer.symbol()))  # ;

        self.jack_tokenizer.advance()
