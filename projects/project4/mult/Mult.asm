// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

//pseudo code
//int R2 = R1;
// if (R1 == 0){
// goto end
//}
//int R2 = R0;
//int n = R1;
//int i = 1;
//while (i < n) {
//  R2 = R2 + R0;
//  i++;
//}

@R1
D=M
@R2
M=D //RAM2 = RAM1
@R1
D=M
@END
D;JEQ //D==0 goto END

@R0
D=M
@R2
M=D  //RAM2 = RAM0

@i
M=1 //i =1

(LOOP)
  @i
  D=M
  @R1
  D=D-M  //D=i-RAM1
  @END
  D;JGE // if i-RAM1 >= 0 goto END
  @R0
  D=M
  @R2
  M=D+M //RAM2 = RAM2 + RAM0
  @i
  M=M+1 //i = i+1
  @LOOP
  0;JMP //goto LOOP
(END)
  @END
  0;JMP //infinite loop
