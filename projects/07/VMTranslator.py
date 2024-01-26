import sys

def main():
    output = str()
    file_name = sys.argv[1].split("/")[-1][:-3]
    jump_var = 0
    for line in open(sys.argv[1], 'r').readlines():
        line = line.strip()
        if not line or line[0] == "/":
            continue
        segments = line.split()
        output += "// " + line + "\n"
        if segments[0] == "push":
            output += push(segments, file_name)
        elif segments[0] == "pop":
            output += pop(segments, file_name)
        elif segments[0] == "add":
            output += popHelper()
            output += "@13\n"
            output += "M=D\n"
            output += popHelper()
            output += "@13\n"
            output += "D=D+M\n"
            output += pushHelper()
        elif segments[0] == "sub":
            output += popHelper()
            output += "@13\n"
            output += "M=D\n"
            output += popHelper()
            output += "@13\n"
            output += "D=D-M\n"
            output += pushHelper()
        elif segments[0] == "neg":
            output += popHelper()
            output += "D=-D\n"
            output += pushHelper()
        elif segments[0] == "eq":
            output += popHelper()
            output += "@13\n"
            output += "M=D\n"
            output += popHelper()
            output += "@13\n"
            output += "D=D-M\n"
            output += "@JUMP_" + str(jump_var) + "\n"
            output += "D;JEQ\n"
            output += "D=0\n"
            output += "@NO_JUMP_" + str(jump_var) + "\n"
            output += "0;JMP\n"
            output += "(JUMP_" + str(jump_var) + ")\n"
            output += "D=-1\n"
            output += "(NO_JUMP_" + str(jump_var) + ")\n"
            output += pushHelper()
        elif segments[0] == "gt":
            output += popHelper()
            output += "@13\n"
            output += "M=D\n"
            output += popHelper()
            output += "@13\n"
            output += "D=D-M\n"
            output += "@JUMP_" + str(jump_var) + "\n"
            output += "D;JGT\n"
            output += "D=0\n"
            output += "@NO_JUMP_" + str(jump_var) + "\n"
            output += "0;JMP\n"
            output += "(JUMP_" + str(jump_var) + ")\n"
            output += "D=-1\n"
            output += "(NO_JUMP_" + str(jump_var) + ")\n"
            output += pushHelper()
        elif segments[0] == "lt":
            output += popHelper()
            output += "@13\n"
            output += "M=D\n"
            output += popHelper()
            output += "@13\n"
            output += "D=D-M\n"
            output += "@JUMP_" + str(jump_var) + "\n"
            output += "D;JLT\n"
            output += "D=0\n"
            output += "@NO_JUMP_" + str(jump_var) + "\n"
            output += "0;JMP\n"
            output += "(JUMP_" + str(jump_var) + ")\n"
            output += "D=-1\n"
            output += "(NO_JUMP_" + str(jump_var) + ")\n"
            output += pushHelper()
        elif segments[0] == "and":
            output += popHelper()
            output += "@13\n"
            output += "M=D\n"
            output += popHelper()
            output += "@13\n"
            output += "D=D&M\n"
            output += pushHelper()
        elif segments[0] == "or":
            output += popHelper()
            output += "@13\n"
            output += "M=D\n"
            output += popHelper()
            output += "@13\n"
            output += "D=D|M\n"
            output += pushHelper()
        elif segments[0] == "not":
            output += popHelper()
            output += "D=!D\n"
            output += pushHelper()
        jump_var += 1
    asm_file = open(sys.argv[1][:-3] + ".asm", "w")
    asm_file.write(output)

# local, argument, this, that, constant, static, temp, pointer
type_dict = {
    "local": "LCL",
    "argument": "ARG", 
    "this": "THIS", 
    "that": "THAT"
}

# Take from segment memory and put on stack
def push(segments, file_name: str) -> str:
    output = str()
    if segments[1] == "constant":
        output += "@" + segments[2] + "\n"
        output += "D=A\n"
        output += pushHelper()
    elif segments[1] == "local" or segments[1] == "argument" or segments[1] == "this" or segments[1] == "that":
        output += "@" + segments[2] + "\n"
        output += "D=A\n"
        output += "@" + type_dict.get(segments[1]) + "\n"
        output += "A=D+M\n"
        output += "D=M\n"
        output += pushHelper()
    elif segments[1] == "static":
        output += "@" + file_name + "." + segments[2] + "\n"
        output += "D=M\n"
        output += pushHelper()
    elif segments[1] == "temp":
        address = int(segments[2]) + 5
        output += "@" + str(address) + "\n"
        output += "D=M\n"
        output += pushHelper()
    elif segments[1] == "pointer":
        if (segments[2] == "0"):
            # THIS
            output += "@THIS\n"
            output += "D=M\n"
            output += pushHelper()
        else:
            # THAT
            output += "@THAT\n"
            output += "D=M\n"
            output += pushHelper()
    return output
    

# Helper for taking D and putting onto the stack, 
# then advancing the stack pointer
def pushHelper() -> str:
    output = str()
    output += "@SP\n"
    output += "A=M\n"
    output += "M=D\n"
    output += "@SP\n"
    output += "M=M+1\n"
    return output


# Take from stack and put in segment memory
def pop(segments, file_name: str) -> str:
    output = str()
    output += popHelper()
    if segments[1] == "local" or segments[1] == "argument" or segments[1] == "this" or segments[1] == "that":
        output += segmentLoader(segments[1], segments[2])
    elif segments[1] == "static":
        output += "@" + file_name + "." + segments[2] + "\n"
        output += "M=D\n"
    elif segments[1] == "temp":
        address = int(segments[2]) + 5
        output += "@" + str(address) + "\n"
        output += "M=D\n"
    elif segments[1] == "pointer":
        if (segments[2] == "0"):
            output += "@THIS\n"
        else:
            output += "@THAT\n"
        output += "M=D\n"
    return output


# Helper for taking from stack, 
# assigning to D, 
# then moving the stack pointer back
def popHelper() -> str:
    output = str()
    output += "@SP\n"
    output += "M=M-1\n"
    output += "A=M\n"
    output += "D=M\n"
    return output


# Helper for assigning D to temp memory 13,
# getting the memory address using temp memory 14 and segment index, 
# then putting it in the address
def segmentLoader(type: str, address: str) -> str:
    output = str()
    output += "@13\n"
    output += "M=D\n"
    output += "@" + address + "\n"
    output += "D=A\n"
    output += "@14\n"
    output += "M=D\n"
    output += "@" + type_dict.get(type) + "\n"
    output += "D=M\n"
    output += "@14\n"
    output += "M=D+M\n"
    output += "@13\n"
    output += "D=M\n"
    output += "@14\n"
    output += "A=M\n"
    output += "M=D\n"
    return output

if __name__ == "__main__":
    print("Translating VM file: " + sys.argv[1])
    main()
