// Setup initial values
	@i
	M=0 // Setup registry i = 0
	@R2
	M=0 // Setup R2 as 0


// Loop for i < R1 and add R0 to D
(LOOP)
	@i
	M=M+1 // Add 1 to i
	D=M // Set data to i
	@R1
	D=D-M // data = data - R1
	@END
	D;JGT // Check if data is 0, go to end for end of loop
	@R0
	D=M // Set current D = R0
	@R2
	M=M+D // Add R0 to R2
	@LOOP
	0;JMP // Goto LOOP

(END)
	@END
	0;JMP
