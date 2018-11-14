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
  @KBD
  D = M //getting value from keyboard register
  @WHITE //proc for white screen
  D; JEQ // if D == 0 fill screen WHITE
  @BLACK // proc for black screen
  0; JMP // go to black screen as part of else

(WHITE)
  @SCREEN
  D= A
  @addr
  M=D //initialize M to the screen base address
  (LOOP1)
  @addr
  D = M
  @KBD
  D = D-A
  @LOOP
  D; JEQ //exit condition for loop when the display map has reached keyboard value
  @addr
  A = M
  M = 0 //filling with white space
  @addr
  M = M + 1 //updating address to the next value
  @LOOP1
  0;JMP

(BLACK)
  @SCREEN
  D= A
  @addr
  M=D //initialize M to the screen base address
  (LOOP2)
  @addr
  D = M
  @KBD
  D = D-A
  @LOOP
  D; JEQ //exit condition for loop when the display map has reached keyboard value
  @addr
  A = M
  M = -1 //filling with black space
  @addr
  M = M + 1 //updating address to the next value
  @LOOP2
  0;JMP
