"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class SymbolTable:
    """
    A symbol table that keeps a correspondence between symbolic labels and 
    numeric addresses.
    """

    symbol_dict = dict()

    def __init__(self) -> None:
        """Creates a new symbol table initialized with all the predefined symbols
        and their pre-allocated RAM addresses, according to section 6.2.3 of the
        book.
        """
        self.symbol_dict["R0"] = 0
        self.symbol_dict["R1"] = 1
        self.symbol_dict["R2"] = 2
        self.symbol_dict["R3"] = 3
        self.symbol_dict["R4"] = 4
        self.symbol_dict["R5"] = 5
        self.symbol_dict["R6"] = 6
        self.symbol_dict["R7"] = 7
        self.symbol_dict["R8"] = 8
        self.symbol_dict["R9"] = 9
        self.symbol_dict["R10"] = 10
        self.symbol_dict["R11"] = 11
        self.symbol_dict["R12"] = 12
        self.symbol_dict["R13"] = 13
        self.symbol_dict["R14"] = 14
        self.symbol_dict["R15"] = 15
        self.symbol_dict["SCREEN"] = 16384
        self.symbol_dict["KBD"] = 24576
        self.symbol_dict["SP"] = 0
        self.symbol_dict["LCL"] = 1
        self.symbol_dict["ARG"] = 2
        self.symbol_dict["THIS"] = 3
        self.symbol_dict["THAT"] = 4

    def add_entry(self, symbol: str, address: int) -> None:
        """Adds the pair (symbol, address) to the table.

        Args:
            symbol (str): the symbol to add.
            address (int): the address corresponding to the symbol.
        """
        self.symbol_dict[symbol] = address


    def contains(self, symbol: str) -> bool:
        """Does the symbol table contain the given symbol?

        Args:
            symbol (str): a symbol.

        Returns:
            bool: True if the symbol is contained, False otherwise.
        """
        return symbol in self.symbol_dict.keys()

    def get_address(self, symbol: str) -> int:
        """Returns the address associated with the symbol.

        Args:
            symbol (str): a symbol.

        Returns:
            int: the address associated with the symbol.
        """
        return self.symbol_dict[symbol]
