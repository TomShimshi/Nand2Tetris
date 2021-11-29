// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 

// Put your code here.

// counter = Array.length (R15)
@R15
D=M
@counter
M=D
(LOOP1)
    // Checks if we finish n iterations
    @counter
    D=M
    @END
    D;JLE
    // counter -= 1
    @counter
    M=M-1
    // i = -1
    @i
    M=-1
(LOOP2)
    // i += 1
    @i
    M=M+1
    // Checks if we are in the last element of the array- R15-i-1
    @R15
    D=M
    @i
    D=D-M
    D=D-1
    // If yes- go back to loop 1
    @LOOP1
    D;JLE
    // Define HEAD index- R14 + i
    @R14
    D=M
    @i
    D=D+M
    @headIndex
    M=D
    // Define headIndex + 1
    @headIndex
    D=M
    @headIndexP1
    M=D+1
    // Define HEAD value
    A=D // Need to check that D doesnt change
    D=M
    @headVal
    M=D
    // Get headIndex + 1 value
    @headIndexP1
    D=M
    A=D
    D=M
    @headVal
    D=D-M
    // If headVal+1 - headVal <= 0 -> go to LOOP2 next iteration
    @LOOP2
    D;JLE
    // Else- do switch and then go to LOOP2 next iteration
    @headIndexP1
    A=M
    D=M
    @temp // headIndex+1 Val
    M=D
    @headIndex
    A=M
    D=M
    @headIndexP1
    A=M
    M=D
    @temp
    D=M
    @headIndex
    A=M
    M=D
    @LOOP2
    0;JMP
(END)
    // Infinity loop
    @END
    0;JMP
