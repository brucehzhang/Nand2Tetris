// function Sys.init 0
(Sys.init)
// push constant 4000	// tests that THIS and THAT are handled correctly
@4000
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 0
@SP
M=M-1
A=M
D=M
@THIS
M=D
// push constant 5000
@5000
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 1
@SP
M=M-1
A=M
D=M
@THAT
M=D
// call Sys.main 0
@Sys.main5.ret
D=A
@LCL
D=M
@ARG
D=M
@THIS
D=M
@THAT
D=M
@5
D=A
@0
D=D+A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.main
0;JMP
(Sys.main5.ret)
// pop temp 1
@SP
M=M-1
A=M
D=M
@6
M=D
// label LOOP
(LOOP)
// goto LOOP
@LOOP
0;JMP
// function Sys.main 5
(Sys.main)
// push constant 4001
@4001
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 0
@SP
M=M-1
A=M
D=M
@THIS
M=D
// push constant 5001
@5001
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 1
@SP
M=M-1
A=M
D=M
@THAT
M=D
// push constant 200
@200
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop local 1
@SP
M=M-1
A=M
D=M
@13
M=D
@1
D=A
@14
M=D
@LCL
D=M
@14
M=D+M
@13
D=M
@14
A=M
M=D
// push constant 40
@40
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop local 2
@SP
M=M-1
A=M
D=M
@13
M=D
@2
D=A
@14
M=D
@LCL
D=M
@14
M=D+M
@13
D=M
@14
A=M
M=D
// push constant 6
@6
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop local 3
@SP
M=M-1
A=M
D=M
@13
M=D
@3
D=A
@14
M=D
@LCL
D=M
@14
M=D+M
@13
D=M
@14
A=M
M=D
// push constant 123
@123
D=A
@SP
A=M
M=D
@SP
M=M+1
// call Sys.add12 1
@Sys.add1221.ret
D=A
@LCL
D=M
@ARG
D=M
@THIS
D=M
@THAT
D=M
@5
D=A
@1
D=D+A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.add12
0;JMP
(Sys.add1221.ret)
// pop temp 0
@SP
M=M-1
A=M
D=M
@5
M=D
// push local 0
@0
D=A
@LCL
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push local 1
@1
D=A
@LCL
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push local 2
@2
D=A
@LCL
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push local 3
@3
D=A
@LCL
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push local 4
@4
D=A
@LCL
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@13
M=D
@SP
M=M-1
A=M
D=M
@13
D=D+M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@13
M=D
@SP
M=M-1
A=M
D=M
@13
D=D+M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@13
M=D
@SP
M=M-1
A=M
D=M
@13
D=D+M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@13
M=D
@SP
M=M-1
A=M
D=M
@13
D=D+M
@SP
A=M
M=D
@SP
M=M+1
// return
@LCL
D=M
@13
M=D
@5
A=D-A
D=M
@14
M=D
@ARG
A=M
M=D
@ARG
D=A+1
@SP
M=D
@13
D=M-1
@THAT
M=D
D=D-1
@THIS
M=D
D=D-1
@ARG
M=D
D=D-1
@LCL
M=D
@14
A=M
0;JMP
// function Sys.add12 0
(Sys.add12)
// push constant 4002
@4002
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 0
@SP
M=M-1
A=M
D=M
@THIS
M=D
// push constant 5002
@5002
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 1
@SP
M=M-1
A=M
D=M
@THAT
M=D
// push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 12
@12
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@13
M=D
@SP
M=M-1
A=M
D=M
@13
D=D+M
@SP
A=M
M=D
@SP
M=M+1
// return
@LCL
D=M
@13
M=D
@5
A=D-A
D=M
@14
M=D
@ARG
A=M
M=D
@ARG
D=A+1
@SP
M=D
@13
D=M-1
@THAT
M=D
D=D-1
@THIS
M=D
D=D-1
@ARG
M=D
D=D-1
@LCL
M=D
@14
A=M
0;JMP