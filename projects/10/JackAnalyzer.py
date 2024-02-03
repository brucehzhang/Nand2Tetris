import os
import sys
from xml.etree import ElementTree as ET

def main():
    if (len(sys.argv) == 2):
        for root, dirs, files in os.walk("."):
            if (sys.argv[1].endswith(".jack")):
                for name in files:
                    if name == sys.argv[1].split("/")[-1]:
                        token_xml = tokenize(os.path.join(root, name))
                        # parse(ET.parse(token_xml))
            else:
                if (root.endswith(sys.argv[1])):
                    for entry in os.scandir(root):
                        if (entry.name.endswith(".jack")):
                            token_xml = tokenize(os.path.join(root, entry.name))
                            # parse(ET.parse(token_xml))
    else:
        for entry in os.scandir():
            if (entry.name.endswith(".jack")):
                token_xml = tokenize(entry.name)
                # parse(ET.parse(token_xml))


def tokenize(file_path: str) -> str:
    print(file_path)
    root = ET.Element("tokens")
    file_content = open(file_path, 'r').read()
    tokenize_helper(file_content, root)
    token_xml_file_path = file_path[:-5] + "T.xml"
    print(token_xml_file_path)
    ET.ElementTree(root).write(token_xml_file_path)
    return token_xml_file_path


def tokenize_helper(file_content: str, root_element: ET.Element):
    token = str()
    is_string = False
    for curr in file_content:
        if is_string:
            # Handle string constants
            if curr == '"':
                is_string = False
                string_element = ET.Element("stringConstant")
                string_element.text = token
                root_element.append(string_element)
                token = str()
            else:
                token += curr
        elif token == "//":
            # Handle single-line comments
            if curr == '\n':
                token = str()
        elif token.startswith("/*"):
            # Handle multi-line comments
            token += curr
            if token.endswith("*/"):
                token = str()
        elif curr == '"':
            # Handle starting a string constant
            is_string = True
        elif curr == ' ':
            # Handle white space and determine if token or not
            if len(token) > 0:
                # Token found, append to root
                found_token(token, root_element)
                token = str()
        elif curr == '\n':
            # Handle line break
            continue
        elif curr in lexical_dict:
            # Handle statement end
            if len(token) > 0:
                # Token found, append to root
                found_token(token, root_element)
                found_token(curr, root_element)
                token = str()
        else:
            token += curr

def found_token(token: str, root_element: ET.Element):
    type = str()
    if token in lexical_dict:
        type = lexical_dict.get(token)
    elif token.isdigit():
        type = "integerConstant"
    else:
        type = "identifier"
    element = ET.Element(type)
    element.text = token
    root_element.append(element)

def parse(token_xml: ET.ElementTree):
    element = token_xml.getroot()

lexical_dict = {
    "class": "keyword",
    "constructor": "keyword",
    "function": "keyword",
    "method": "keyword",
    "field": "keyword",
    "static": "keyword",
    "var": "keyword",
    "int": "keyword",
    "char": "keyword",
    "boolean": "keyword",
    "void": "keyword",
    "true": "keyword",
    "false": "keyword",
    "null": "keyword",
    "this": "keyword",
    "let": "keyword",
    "do": "keyword",
    "if": "keyword",
    "else": "keyword",
    "while": "keyword",
    "return": "keyword",
    "{": "symbol",
    "}": "symbol",
    "(": "symbol",
    ")": "symbol",
    "[": "symbol",
    "]": "symbol",
    ".": "symbol",
    ",": "symbol",
    ";": "symbol",
    "+": "symbol",
    "-": "symbol",
    "*": "symbol",
    "/": "symbol",
    "&": "symbol",
    "|": "symbol",
    "<": "symbol",
    ">": "symbol",
    "=": "symbol",
    "~": "symbol",
}

recursive_set = ["while", "if", "else", "let", "do"]

if __name__ == "__main__":
    if (len(sys.argv) == 2):
        if (sys.argv[1].endswith(".jack")):
            print("Translating Jack file: " + sys.argv[1])
        else:
            print("Translating Jack files for directory: " + sys.argv[1])
    else:
        print("Translating all Jack files in current directory")
    main()