"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """
    keyword_set = {"class", "method", "function", "constructor", "int", "boolean",
                   "char", "void", "var", "static", "field", "let", "do", "if", "else",
                   "while", "return", "true", "false", "null", "this"}

    symbol_set = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*",
                  "/", "&", "|", "<", ">", "=", "~", "^", "#"}

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input_lines = input_stream.read().splitlines()
        self.all_tokens = []
        self.make_tokens_list()

        self.token_count = len(self.all_tokens)
        self.token_counter = 0

    def make_tokens_list(self) -> None:
        """
        Convert self.input lines from list of lines to a list of tokens
        """
        input_file_str = "\n".join(self.input_lines)
        no_comments_file_str = self.remove_comments(input_file_str)
        self.input_lines = no_comments_file_str.split('\n')

        for line in self.input_lines:
            curr_line = line.strip()

            if '"' in curr_line:
                curr_line_lst = curr_line.split('"')
                curr_line_lst = self.line_with_string(curr_line_lst)
                curr_line = '"'.join(curr_line_lst)

            else:
                curr_line = curr_line.replace(" ", "$")
                curr_line = curr_line.replace("   ", "$")
                curr_line = curr_line.replace("\t", "$")
                for symbol in self.symbol_set:
                    curr_line = curr_line.replace(symbol, "${0}$".format(symbol))

            curr_line_lst = curr_line.split("$")

            for token in curr_line_lst:
                if token != "" and token != " ":
                    self.all_tokens.append(token)

    def line_with_string(self, curr_line_lst):
        for i in range(len(curr_line_lst)):
            if i % 2 == 0:
                curr_line_lst[i] = curr_line_lst[i].replace(" ", "$")
                curr_line_lst[i] = curr_line_lst[i].replace("   ", "$")
                curr_line_lst[i] = curr_line_lst[i].replace("\t", "$")
                for symbol in self.symbol_set:
                    curr_line_lst[i] = curr_line_lst[i].replace(symbol, "${0}$".format(symbol))

        return curr_line_lst

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """

        return self.token_counter != self.token_count

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.token_counter += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        curr_token = self.all_tokens[self.token_counter]
        if curr_token in JackTokenizer.keyword_set:
            return "KEYWORD"
        elif curr_token in JackTokenizer.symbol_set:
            return "SYMBOL"
        elif curr_token.isdigit():
            return "INT_CONST"
        elif "'" in curr_token or '"' in curr_token:
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.all_tokens[self.token_counter]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        curr_token = self.all_tokens[self.token_counter]

        if curr_token == '>':
            return "&gt;"
        elif curr_token == '<':
            return "&lt;"
        elif curr_token == '&':
            return "&amp;"
        elif curr_token == '"':
            return "&quot;"
        elif curr_token == '^':
            return "<<"
        elif curr_token == '#':
            return ">>"

        return curr_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.all_tokens[self.token_counter]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return int(self.all_tokens[self.token_counter])

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        to_return = self.all_tokens[self.token_counter]
        if to_return[0] == '"':
            to_return = to_return[1:]
        if to_return and (to_return[-1] == '"'):
            to_return = to_return[:-1]
        return to_return

    def remove_comments(self, input_str: str) -> str:
        """
        Get a string t represents a jack file, and remove all the comments
        :param input_str: string represents input file
        :return:
        """
        started_multiline_comment = False
        started_inline_comment = False
        started_double_quotes = False
        need_to_pass = False

        new_input_str = ""

        for i, val in enumerate(input_str):
            if need_to_pass:
                need_to_pass = False
            elif started_inline_comment:
                if val == "\n":
                    started_inline_comment = False
            elif started_multiline_comment:
                if val == "*" and len(input_str) > i + 1 and input_str[i + 1] == "/":
                    need_to_pass = True
                    started_multiline_comment = False

            elif started_double_quotes:
                if val == '"':
                    started_double_quotes = False
                new_input_str += val

            elif val == '"':
                started_double_quotes = True
                new_input_str += val
            elif val == "/" and len(input_str) > i + 1 and input_str[i + 1] == "/":
                started_inline_comment = True
                need_to_pass = True
            elif val == "/" and len(input_str) > i + 1 and input_str[i + 1] == "*":
                started_multiline_comment = True
                need_to_pass = True
            else:
                new_input_str += val

        return new_input_str
