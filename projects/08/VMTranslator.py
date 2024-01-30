import sys
import os

def main():
    output = str()
    if (len(sys.argv) == 2):
        for root, dirs, files in os.walk("."):
            if (sys.argv[1].endswith(".vm")):
                for name in files:
                    if name == sys.argv[1].split("/")[-1]:
                        output = parser(root, name)
                        file_name = name[:-3]
                        asm_file = open(root + "/" + file_name + ".asm", "w")
                        asm_file.write(output)
            else:
                output += "// System initialization\n"
                output += "@256\n"
                output += "D=A\n"
                output += "@SP\n"
                output += "M=D\n"
                output += call_helper(["call", "Sys.init", "0"], 0)
                if (root.endswith(sys.argv[1])):
                    for entry in os.scandir(root):
                        if (entry.name.endswith(".vm")):
                            output += parser(root, entry.name)
                    if len(output) != 0:
                        asm_file = open(root + "/" + sys.argv[1] + ".asm", "w")
                        asm_file.write(output)
    else:
        for entry in os.scandir():
            if (entry.name.endswith(".vm")):
                output = parser("", entry.name)
                file_name = name[:-3]
                asm_file = open(file_name + ".asm", "w")
                asm_file.write(output)
                

def parser(root: str, name: str) -> str:
    print("Parsing {0}".format(name))
    output = str()
    file_name = name[:-3]
    jump_var = 1
    for line in open(os.path.join(root, name), 'r').readlines():
        line = line.strip()
        if not line or line[0] == "/":
            continue
        segments = line.split()
        output += "// " + line + "\n"
        if segments[0] == "label":
            output += "(" + segments[1] + ")\n"
        elif segments[0] == "goto":
            output += "@" + segments[1] + "\n"
            output += "0;JMP\n"
        elif segments[0] == "if-goto":
            output += pop_helper()
            output += "@" + segments[1] + "\n"
            output += "D;JNE\n"
        elif segments[0] == "function":
            args = int(segments[2])
            # Generate function label
            output += "(" + segments[1] + ")\n"
            # Push LCL with 0 for nvarg times
            for i in range(args):
                output += "@0\n"
                output += "D=A\n"
                output += push_helper()
        elif segments[0] == "call":
            output += call_helper(segments, jump_var)
        elif segments[0] == "return":
            output += return_helper(segments)
        elif segments[0] == "push":
            output += push(segments, file_name)
        elif segments[0] == "pop":
            output += pop(segments, file_name)
        elif segments[0] == "add":
            output += pop_helper()
            output += "@13\n"
            output += "M=D\n"
            output += pop_helper()
            output += "@13\n"
            output += "D=D+M\n"
            output += push_helper()
        elif segments[0] == "sub":
            output += pop_helper()
            output += "@13\n"
            output += "M=D\n"
            output += pop_helper()
            output += "@13\n"
            output += "D=D-M\n"
            output += push_helper()
        elif segments[0] == "neg":
            output += pop_helper()
            output += "D=-D\n"
            output += push_helper()
        elif segments[0] == "eq":
            output += pop_helper()
            output += "@13\n"
            output += "M=D\n"
            output += pop_helper()
            output += "@13\n"
            output += "D=D-M\n"
            output += "@JUMP_" + name + str(jump_var) + "\n"
            output += "D;JEQ\n"
            output += "D=0\n"
            output += "@NO_JUMP_" + name + str(jump_var) + "\n"
            output += "0;JMP\n"
            output += "(JUMP_" + name + str(jump_var) + ")\n"
            output += "D=-1\n"
            output += "(NO_JUMP_" + name + str(jump_var) + ")\n"
            output += push_helper()
        elif segments[0] == "gt":
            output += pop_helper()
            output += "@13\n"
            output += "M=D\n"
            output += pop_helper()
            output += "@13\n"
            output += "D=D-M\n"
            output += "@JUMP_" + name + str(jump_var) + "\n"
            output += "D;JGT\n"
            output += "D=0\n"
            output += "@NO_JUMP_" + name + str(jump_var) + "\n"
            output += "0;JMP\n"
            output += "(JUMP_" + name + str(jump_var) + ")\n"
            output += "D=-1\n"
            output += "(NO_JUMP_" + name + str(jump_var) + ")\n"
            output += push_helper()
        elif segments[0] == "lt":
            output += pop_helper()
            output += "@13\n"
            output += "M=D\n"
            output += pop_helper()
            output += "@13\n"
            output += "D=D-M\n"
            output += "@JUMP_" + name + str(jump_var) + "\n"
            output += "D;JLT\n"
            output += "D=0\n"
            output += "@NO_JUMP_" + name + str(jump_var) + "\n"
            output += "0;JMP\n"
            output += "(JUMP_" + name + str(jump_var) + ")\n"
            output += "D=-1\n"
            output += "(NO_JUMP_" + name + str(jump_var) + ")\n"
            output += push_helper()
        elif segments[0] == "and":
            output += pop_helper()
            output += "@13\n"
            output += "M=D\n"
            output += pop_helper()
            output += "@13\n"
            output += "D=D&M\n"
            output += push_helper()
        elif segments[0] == "or":
            output += pop_helper()
            output += "@13\n"
            output += "M=D\n"
            output += pop_helper()
            output += "@13\n"
            output += "D=D|M\n"
            output += push_helper()
        elif segments[0] == "not":
            output += pop_helper()
            output += "D=!D\n"
            output += push_helper()
        jump_var += 1
    return output


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
        output += push_helper()
    elif segments[1] == "local" or segments[1] == "argument" or segments[1] == "this" or segments[1] == "that":
        output += "@" + segments[2] + "\n"
        output += "D=A\n"
        output += "@" + type_dict.get(segments[1]) + "\n"
        output += "A=D+M\n"
        output += "D=M\n"
        output += push_helper()
    elif segments[1] == "static":
        output += "@" + file_name + "." + segments[2] + "\n"
        output += "D=M\n"
        output += push_helper()
    elif segments[1] == "temp":
        address = int(segments[2]) + 5
        output += "@" + str(address) + "\n"
        output += "D=M\n"
        output += push_helper()
    elif segments[1] == "pointer":
        if (segments[2] == "0"):
            # THIS
            output += "@THIS\n"
            output += "D=M\n"
            output += push_helper()
        else:
            # THAT
            output += "@THAT\n"
            output += "D=M\n"
            output += push_helper()
    return output
    

def call_helper(segments: list, jump_var: int) -> str:
    args = int(segments[2])
    # Push return address
    output = "@" + segments[1] + str(jump_var) + ".ret\n"
    output += "D=A\n"
    output += push_helper()
    # Push LCL
    output += "@LCL\n"
    output += "D=M\n"
    output += push_helper()
    # Push ARG
    output += "@ARG\n"
    output += "D=M\n"
    output += push_helper()
    # Push THIS
    output += "@THIS\n"
    output += "D=M\n"
    output += push_helper()
    # Push THAT
    output += "@THAT\n"
    output += "D=M\n"
    output += push_helper()
    # Reposition ARG
    output += "@SP\n"
    output += "D=M\n"
    output += "@" + str(args + 5) + "\n"
    output += "D=D-A\n"
    output += "@ARG\n"
    output += "M=D\n"
    # Reposition LCL
    output += "@SP\n"
    output += "D=M\n"
    output += "@LCL\n"
    output += "M=D\n"
    # Jump to function
    output += "@" + segments[1] + "\n"
    output += "0;JMP\n"
    # Return address
    output += "(" + segments[1] + str(jump_var) + ".ret)\n"
    return output


def return_helper(segments: list) -> str:
    output = "@LCL\n"
    output += "D=M\n"
    # Endframe
    output += "@EndFrame\n"
    output += "M=D\n"
    output += "@5\n"
    output += "A=D-A\n"
    output += "D=M\n"
    # Return Address
    output += "@ReturnAddr\n"
    output += "M=D\n"
    output += pop_helper()
    output += "@ARG\n"
    output += "A=M\n"
    output += "M=D\n"
    output += "@ARG\n"
    output += "D=M+1\n"
    output += "@SP\n"
    output += "M=D\n"
    # Restore THAT
    output += "@EndFrame\n"
    output += "D=M\n"
    output += "@1\n"
    output += "D=D-A\n"
    output += "A=D\n"
    output += "D=M\n"
    output += "@THAT\n"
    output += "M=D\n"
    # Restore THIS
    output += "@EndFrame\n"
    output += "D=M\n"
    output += "@2\n"
    output += "D=D-A\n"
    output += "A=D\n"
    output += "D=M\n"
    output += "@THIS\n"
    output += "M=D\n"
    # Restore ARG
    output += "@EndFrame\n"
    output += "D=M\n"
    output += "@3\n"
    output += "D=D-A\n"
    output += "A=D\n"
    output += "D=M\n"
    output += "@ARG\n"
    output += "M=D\n"
    # Restore LCL
    output += "@EndFrame\n"
    output += "D=M\n"
    output += "@4\n"
    output += "D=D-A\n"
    output += "A=D\n"
    output += "D=M\n"
    output += "@LCL\n"
    output += "M=D\n"
    # Goto Return Address
    output += "@ReturnAddr\n"
    output += "A=M\n"
    output += "0;JMP\n"
    return output

# Helper for taking D and putting onto the stack, 
# then advancing the stack pointer
def push_helper() -> str:
    output = "@SP\n"
    output += "A=M\n"
    output += "M=D\n"
    output += "@SP\n"
    output += "M=M+1\n"
    return output


# Take from stack and put in segment memory
def pop(segments, file_name: str) -> str:
    output = pop_helper()
    if segments[1] == "local" or segments[1] == "argument" or segments[1] == "this" or segments[1] == "that":
        output += segment_loader(segments[1], segments[2])
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
def pop_helper() -> str:
    output = "@SP\n"
    output += "M=M-1\n"
    output += "A=M\n"
    output += "D=M\n"
    return output


# Helper for assigning D to temp memory 13,
# getting the memory address using temp memory 14 and segment index, 
# then putting it in the address
def segment_loader(type: str, address: str) -> str:
    output = "@13\n"
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
    if (len(sys.argv) == 2):
        if (sys.argv[1].endswith(".vm")):
            print("Translating VM file: " + sys.argv[1])
        else:
            print("Translating VM files for directory or file: " + sys.argv[1])
    else:
        print("Translating all VM files")
    main()
