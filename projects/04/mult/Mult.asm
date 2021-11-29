// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

    // sum = 0
    @sum
    M=0
    // i = R1
    @R1
    D=M
    @i
    M=D
(LOOP)
    @i
    D=M
    // if i == 0 then go to stop
    @STOP
    D;JEQ
    //sum += R0
    @sum
    D=M
    @R0
    D=D+M
    @sum
    M=D
    //i -= 1
    @i
    M=M-1
    @LOOP
    0;JMP
(STOP)
    // R2 = sum
    @sum
    D=M
    @R2
    M=D
(END)
    // Infinity loop
    @END
    0;JMP
