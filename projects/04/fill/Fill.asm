// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(LOOP)
    // define i=8191 -> 0
    @8191
    D=A
    @i
    M=D
    // check if any key is pressed
    @KBD
    D=M
    @WHITELOOP
    D;JEQ
    @BLACKLOOP
    D;JNE
(WHITELOOP)
    @i
    D=M
    @LOOP
    D;JLT
    @SCREEN
    D=D+A
    @currCell
    A=D
    M=0
    @i
    M=M-1
    @WHITELOOP
    0;JMP
(BLACKLOOP)
    @i
    D=M
    @LOOP
    D;JLT
    @SCREEN
    D=D+A
    @currCell
    A=D
    M=-1
    @i
    M=M-1
    @BLACKLOOP
    0;JMP

(END)
    // Infinity loop
    @END
    0;JMP


