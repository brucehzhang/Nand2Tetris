from io import TextIOWrapper
import os

def parse(name: str):
    asm_file = open(os.path.join(root, name), 'r').readlines()
    symbols = {
        "R0": 0, 
        "R1": 1,
        "R2": 2,
        "R3": 3,
        "R4": 4,
        "R5": 5,
        "R6": 6,
        "R7": 7,
        "R8": 8,
        "R9": 9,
        "R10": 10,
        "R11": 11,
        "R12": 12,
        "R13": 13,
        "R14": 14,
        "R15": 15,
        "SCREEN": 16384,
        "KBD": 24576,
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4
        }
    first_pass(asm_file, symbols)
    hack_file = open(name[:-4] + ".hack", "w")
    hack_file.write(second_pass(asm_file, symbols))


def first_pass(file: list[str], symbols: dict):
    i = 0
    for line in file:
        line = line.strip()
        if not line or line[0] == "/":
            continue
        elif line[0] == "(":
            symbols[line[1:-1]] = i
        else:
            i += 1


def second_pass(file: list[str], symbols: dict) -> str:
    output = ""
    i = 16
    for line in file:
        line = line.strip()
        if not line or line[0] == "/" or line[0] == "(":
            continue
        elif line[0] == "@":
            if line[1:] in symbols:
                output += a_instruction(symbols.get(line[1:])) + "\n"
            elif line[1:].isnumeric():
                output += a_instruction(int(line[1:])) + "\n"
            else:
                symbols[line[1:]] = i
                output += a_instruction(i) + "\n"
                i += 1
        else:
            output += c_instruction(line) + "\n"
    return output



def a_instruction(address: int) -> str:
    return format(address, '016b')


def c_instruction(line: str) -> str:
    output = "111"
    if "=" in line and ";" in line:
        # has dest and jump
        segments = line.split(["=", ";"])
        output += comp_table.get(segments[1])
        output += dest_table.get(segments[0])
        output += jump_table.get(segments[2])
    elif "=" in line:
        # has dest
        segments = line.split("=")
        output += comp_table.get(segments[1])
        output += dest_table.get(segments[0])
        output += "000"
    elif ";" in line:
        # has jump
        segments = line.split(";")
        output += comp_table.get(segments[0])
        output += "000"
        output += jump_table.get(segments[1])
    else:
        raise Exception("Invalid C instruction found: {0}".format(line))
    return output

comp_table = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001111",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101"
}


dest_table = {
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}


jump_table = {
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}

for root, dirs, files in os.walk("."):
    for name in files:
        if name.endswith(".asm"):
            print("Parsing {0}".format(name))
            parse(name)
