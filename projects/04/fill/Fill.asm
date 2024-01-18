// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(LOOP)
	@SCREEN
	D=A // Store address of screen
	@addr
	M=D
	@i
	M=0
	@KBD
	D=M; // Get keyboard output
	@FILL
	D;JNE // If keyboard output != 0, jump to fill
	@UNFILL
	0;JMP // Else, jump to unfill
	
	(FILL)
		@i
		D=M // Set data to i
		@addr
		A=M+D // Get starting address + i
		M=-1 // Set 16 bits to black
		@i
		M=M+1 // Increment i
		D=M // Set data to i
		@8192
		D=D-A // Set data to data - 8192
		@FILL
		D;JLT // Loop to FILL if data > 0
		@LOOP
		0;JMP // Goto LOOP

	(UNFILL)
		@i
		D=M // Set data to i
		@addr
		A=M+D // Get starting address + i
		M=0 // Set 16 bits to white
		@i
		M=M+1 // Increment
		D=M // Set data to i
		@8192
		D=D-A // Set data to data - 8192
		@UNFILL
		D;JLT // Loop to FILL if data > 0
		@LOOP
		0;JMP // Goto LOOP
	

