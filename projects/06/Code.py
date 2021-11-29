"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""

    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        if mnemonic == "M":
            return "001"
        elif mnemonic == "D":
            return "010"
        elif mnemonic == "MD":
            return "011"
        elif mnemonic == "A":
            return "100"
        elif mnemonic == "AM":
            return "101"
        elif mnemonic == "AD":
            return "110"
        elif mnemonic == "AMD":
            return "111"
        else:
            return "000"

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: 7-bit long binary code of the given mnemonic.
        """
        if mnemonic == "0":
            return "0101010"
        elif mnemonic == "1":
            return "0111111"
        elif mnemonic == "-1":
            return "0111010"
        elif mnemonic == "D":
            return "0001100"
        elif mnemonic == "A":
            return "0110000"
        elif mnemonic == "M":
            return "1110000"
        elif mnemonic == "!D":
            return "0001101"
        elif mnemonic == "!A":
            return "0110001"
        elif mnemonic == "!M":
            return "1110001"
        elif mnemonic == "-D":
            return "0001111"
        elif mnemonic == "-A":
            return "0110011"
        elif mnemonic == "-M":
            return "1110011"
        elif mnemonic == "D+1":
            return "0011111"
        elif mnemonic == "A+1":
            return "0110111"
        elif mnemonic == "M+1":
            return "1110111"
        elif mnemonic == "D-1":
            return "0001110"
        elif mnemonic == "A-1":
            return "0110010"
        elif mnemonic == "M-1":
            return "1110010"
        elif mnemonic == "D+A":
            return "0000010"
        elif mnemonic == "D+M":
            return "1000010"
        elif mnemonic == "D-A":
            return "0010011"
        elif mnemonic == "D-M":
            return "1010011"
        elif mnemonic == "A-D":
            return "0000111"
        elif mnemonic == "M-D":
            return "1000111"
        elif mnemonic == "D&A":
            return "0000000"
        elif mnemonic == "D&M":
            return "1000000"
        elif mnemonic == "D|A":
            return "0010101"
        elif mnemonic == "D|M":
            return "1010101"
        elif mnemonic == "D<<":
            return "0110000"
        elif mnemonic == "A<<":
            return "0100000"
        elif mnemonic == "M<<":
            return "1100000"
        elif mnemonic == "D>>":
            return "0010000"
        elif mnemonic == "A>>":
            return "0000000"
        elif mnemonic == "M>>":
            return "1000000"



    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        if mnemonic == "JGT":
            return "001"
        elif mnemonic == "JEQ":
            return "010"
        elif mnemonic == "JGE":
            return "011"
        elif mnemonic == "JLT":
            return "100"
        elif mnemonic == "JNE":
            return "101"
        elif mnemonic == "JLE":
            return "110"
        elif mnemonic == "JMP":
            return "111"
        else:
            return "000"
