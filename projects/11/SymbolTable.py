"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_dict = {}
        self.subroutine_dict = {}

        self.field_index = 0
        self.static_index = 0
        self.var_index = 0
        self.arg_index = 0

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_dict = {}
        self.var_index = 0
        self.arg_index = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "static", "field", "argument", "var".
        """
        if kind in ["field", "static"]:
            if kind == "field":
                index = self.field_index
                self.field_index += 1
            else:
                index = self.static_index
                self.static_index += 1
            self.class_dict[name] = [type, kind, index]

        else:
            if kind == "argument":
                index = self.arg_index
                self.arg_index += 1
            else:
                index = self.var_index
                self.var_index += 1
            self.subroutine_dict[name] = [type, kind, index]


    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind == "field":
            return self.field_index
        elif kind == "static":
            return self.static_index
        elif kind == "argument":
            return self.arg_index
        else:
            return self.var_index

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or
            None if the identifier is unknown in the current scope.
        """

        if name in self.subroutine_dict:
            return self.subroutine_dict[name][1]
        elif name in self.class_dict:
            return self.class_dict[name][1]
        else:
            return None

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.subroutine_dict:
            return self.subroutine_dict[name][0]
        elif name in self.class_dict:
            return self.class_dict[name][0]
        else:
            return None

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.subroutine_dict:
            return self.subroutine_dict[name][2]
        elif name in self.class_dict:
            return self.class_dict[name][2]
        else:
            return None
