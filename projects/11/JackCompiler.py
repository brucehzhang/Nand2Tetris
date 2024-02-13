from io import TextIOWrapper
import os
import sys
import uuid
from xml.etree import ElementTree as ET

class_table = {}
field_index = 0
static_index = 0

subroutine_table = {}
argument_index = 0
local_index = 0

class_name = None

curr_vm_file: TextIOWrapper = None

math_dict = {
    "+": "add",
    "-": "sub",
    "*": "call Math.multiply 2",
    "/": "call Math.divide 2",
    "&lt;": "lt",
    "&gt;": "gt",
    "=": "eq"
}

def main():
    global class_name
    global curr_vm_file
    if (len(sys.argv) == 2):
        for root, dirs, files in os.walk("."):
            if (sys.argv[1].endswith(".jack")):
                for name in files:
                    if name == sys.argv[1].split("/")[-1]:
                        token_xml_file_path = tokenize(os.path.join(root, name))
                        class_name = name[:-5]
                        curr_vm_file = open(os.path.join(root, name[:-5] + ".vm"), "w")
                        compile_vm_code(token_xml_file_path)
                        curr_vm_file.close()
            else:
                if (root.split("/")[-1] == (sys.argv[1])):
                    for entry in os.scandir(root):
                        if (entry.name.endswith(".jack")):
                            token_xml_file_path = tokenize(os.path.join(root, entry.name))
                            class_name = entry.name[:-5]
                            curr_vm_file = open(os.path.join(root, entry.name[:-5] + ".vm"), "w")
                            compile_vm_code(token_xml_file_path)
                            curr_vm_file.close()
    else:
        for entry in os.scandir():
            if (entry.name.endswith(".jack")):
                token_xml_file_path = tokenize(entry.name)
                class_name = entry.name[:-5]
                curr_vm_file = open(entry.name[:-5] + ".vm", "w")
                compile_vm_code(token_xml_file_path)
                curr_vm_file.close()


def tokenize(file_path: str) -> str:
    root = ET.Element("tokens")
    file_content = open(file_path, 'r').read()
    tokenize_helper(file_content, root)
    token_xml_file_path = file_path[:-5] + "T.xml"
    ET.indent(root, space="\t", level=0)
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
        elif token == "/":
            if curr == "/" or curr == "*":
                token += curr
            else:
                found_token("/", root_element)
                token = str()
        elif token.startswith("//"):
            # Handle single-line comments
            token += curr
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
        elif curr == ' ' or curr == '	':
            # Handle white space and determine if token or not
            if len(token) > 0:
                # Token found, append to root
                found_token(token, root_element)
                token = str()
        elif curr == '\n':
            # Handle line break
            continue
        elif curr in lexical_dict and not curr == "/":
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


def compile_vm_code(token_xml_file_path: str):
    token_root = ET.parse(token_xml_file_path).getroot()
    token_elements = list(token_root.iter())
    token_elements.reverse()
    compile_class(token_elements)


def compile_class(token_elements: list):
    # Reset class table
    class_table.clear()
    global field_index
    field_index = 0
    global static_index
    static_index = 0
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.tag == "tokens":
            # Ignore since tokens tag isn't needed and class element is already setup
            continue
        elif token_element.text in ["field", "static"]:
            # ClassVarDec
            compile_class_var(token_element, token_elements)
        elif token_element.text in ["constructor", "function", "method"]:
            # SubroutineDec
            compile_subroutine(token_element, token_elements)


def compile_class_var(initial_element: ET.Element, token_elements: list):
    kind = initial_element.text
    type = None
    global field_index
    global static_index
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        # Keyword/Identifier/Symbol only
        if token_element.tag == "keyword":
            type = token_element.text
        elif token_element.tag == "identifier":
            if kind == "field":
                class_table[token_element.text] = {"type": type, "kind": kind, "#": field_index}
                field_index += 1
            elif kind == "static":
                class_table[token_element.text] = {"type": type, "kind": kind, "#": static_index}
                static_index += 1
        if token_element.text == ';':
            return
    raise Exception("Compilation Error: End of tokens during compile_class_var")
        

def compile_subroutine(initial_element: ET.Element, token_elements: list):
    subroutine_table.clear
    global argument_index
    argument_index = 0
    subroutine_name = None
    global local_index
    local_index = 0
    subroutine_type = initial_element.text
    if subroutine_type == "method":
        subroutine_table["this"] = {"type": class_name, "kind": "argument", "#": argument_index}
        argument_index += 1
    curr_vm_file.write("push argument 0\n")
    curr_vm_file.write("pop pointer 0\n")
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.text == "(":
            # ParameterList
            compile_parameter_list(token_elements)
        elif token_element.tag == 'identifier':
            subroutine_name = token_element.text
        elif token_element.text == '{':
            # function class_name.subroutine_name numArgs
            curr_vm_file.write("function " + class_name + "." + subroutine_name + str(argument_index) + "\n")
            # SubroutineBody
            compile_subroutine_body(token_element, token_elements)
            return
    raise Exception("Compilation Error: End of tokens during compile_subroutine")


def compile_parameter_list(token_elements: list):
    type = None
    global argument_index
    while len(token_elements) > 0:
        if token_elements[-1].text == ')':
            # If peeked ')', return to subroutine compilation
            return
        token_element = token_elements.pop()
        if token_element.tag == "keyword":
            type = token_element.text
        elif token_element.tag == "identifier":
            subroutine_table[token_element.text] = {"type": type, "kind": "argument", "#": argument_index}
            argument_index += 1
    raise Exception("Compilation Error: End of tokens during compile_parameter_list")


def compile_subroutine_body(initial_element: ET.Element, token_elements: list):
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.text == "var":
            compile_var_dec(token_element, token_elements)
        elif token_element.text in ["do", "let", "while", "return", "if"]:
            # Statements
            # TODO:: Continue from here
            compile_statements(token_element, token_elements)
        else:
            # Ending '}' symbol
            return
    raise Exception("Compilation Error: End of tokens during compile_subroutine_body")


def compile_var_dec(initial_element: ET.Element, token_elements: list):
    type = None
    global local_index
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.tag == "keyword":
            type = token_element.text
        elif token_element.tag == "identifier":
            subroutine_table[token_element.text] = {"type": type, "kind": "local", "#": local_index}
            local_index += 1
        if token_element.text == ';':
            return
    raise Exception("Compilation Error: End of tokens during compile_var_dec")


def compile_statements(initial_element: ET.Element, token_elements: list):
    curr_local_index = local_index
    # Check initial statement
    if initial_element.text == 'do':
        compile_do(token_elements)
    elif initial_element.text == 'let':
        compile_let(token_elements)
    elif initial_element.text == 'while':
        compile_while(initial_element, token_elements)
    elif initial_element.text == 'return':
        compile_return(token_elements)
    elif initial_element.text == 'if':
        compile_if(token_elements)
    while len(token_elements) > 0:
        if token_elements[-1].text == 'do':
            token_elements.pop()
            compile_do(token_elements)
        elif token_elements[-1].text == 'let':
            token_elements.pop()
            compile_let(token_elements)
        elif token_elements[-1].text == 'while':
            token_elements.pop()
            compile_while(token_elements)
        elif token_elements[-1].text == 'return':
            token_elements.pop()
            compile_return(token_elements)
        elif token_elements[-1].text == 'if':
            token_elements.pop()
            compile_if(token_elements)
        else:
            return
    return


def compile_do(token_elements: list):
    function_name = ""
    arg_count = 0
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.text == '(':
            # ExpressionList
            arg_count = compile_expression_list(token_elements)
        elif token_element.text == ';':
            curr_vm_file.write("call " + function_name + str(arg_count) + "\n")
            return
        elif token_element.tag == 'identifier' or token_element.text == '.':
            function_name += token_element.text
    raise Exception("Compilation Error: End of tokens during compile_do")


def compile_let(token_elements: list):
    global subroutine_table
    global class_table
    assigned_var = ""
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.text == '=' or token_element.text == '[':
            # Expression
            compile_expression(token_elements.pop(), token_elements)
        elif token_element.text == ';':
            # End
            if assigned_var in subroutine_table:
                segment = subroutine_table.get(assigned_var).get("kind")
                index = str(subroutine_table.get(assigned_var).get("#"))
                curr_vm_file.write("pop " + segment + " " + index + "\n")
            else:
                segment = class_table.get(assigned_var).get("kind")
                if segment == "field":
                    segment = "this"
                index = str(class_table.get(assigned_var).get("#"))
                curr_vm_file.write("pop " + segment + " " + index + "\n")
        elif token_element.tag == 'identifier':
            assigned_var = token_element.text
    raise Exception("Compilation Error: End of tokens during compile_let")


def compile_while(token_elements: list):
    l1_label = str(uuid.uuid1())
    l2_label = str(uuid.uuid1())
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.text == '(':
            # Expression
            curr_vm_file.write("label " + l1_label + "\n")
            compile_expression(token_elements.pop(), token_elements)
            curr_vm_file.write("not\n")
            curr_vm_file.write("if-goto " + l2_label + "\n")
        elif token_element.text == '{':
            # Statements
            compile_statements(token_elements.pop(), token_elements)
            curr_vm_file.write("go-to " + l1_label + "\n")
        elif token_element.text == '}':
            curr_vm_file.write("label " + l2_label + "\n")
            return
    raise Exception("Compilation Error: End of tokens during compile_while")


def compile_return(token_elements: list):
    has_return_value = False
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.text == ';':
            # End
            if not has_return_value:
                # dummy value on stack to be popped
                curr_vm_file.write("push constant 0\n")
            curr_vm_file.write("return\n")
        else:
            # Expression
            compile_expression(token_element, token_elements)
    raise Exception("Compilation Error: End of tokens during compile_return")


def compile_if(token_elements: list):
    l1_label = str(uuid.uuid1())
    l2_label = str(uuid.uuid1())
    has_else = False
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.text == '(':
            # Expression
            compile_expression(token_elements.pop(), token_elements)
            curr_vm_file.write("not\n")
            curr_vm_file.write("if-goto " + l1_label + "\n")
        elif token_element.text == '{':
            # Statements
            compile_statements(token_elements.pop(), token_elements)
            if not has_else:
                curr_vm_file.write("goto " + l2_label + "\n")
        elif token_element.text == '}' and token_elements[-1].text != "else":
            if not has_else:
                # l1_label if this was only an if statement without else
                curr_vm_file.write("label " + l1_label + "\n")
            curr_vm_file.write("label " + l2_label + "\n")
            return
        elif token_element.text == "else":
            curr_vm_file.write("label " + l1_label + "\n")
            has_else = True
    raise Exception("Compilation Error: End of tokens during compile_if")


def compile_expression_list(token_elements: list) -> int:
    count = 0
    while len(token_elements) > 0:
        if token_elements[-1].text == ')':            
            # If peeked ')', return to statement compilation
            return count
        token_element = token_elements.pop()
        if token_element.text != ',':
            compile_expression(token_element, token_elements)
            count += 1
    raise Exception("Compilation Error: End of tokens during compile_expression_list")


def compile_expression(initial_element: ET.Element, token_elements: list):
    compile_term(initial_element, token_elements)
    symbols = []
    while len(token_elements) > 0:
        if token_elements[-1].text in [')', ']', ';', ',']:
            # do VM code for math last to enable left to right expression
            for i in range(len(symbols)):
                curr_vm_file.write(math_dict.get(symbols[i]) + "\n")
            return
        elif token_elements[-1].tag == "symbol" and token_elements[-1].text not in ['(', '[']:
            token_element = token_elements.pop()
            if token_element.text in math_dict:
                symbols.append(token_element.text)
        else:
            compile_term(token_elements.pop(), token_elements)
    raise Exception("Compilation Error: End of tokens during compile_expression")


def compile_term(initial_element: ET.Element, token_elements: list):
    compile_element = ET.Element(initial_element.tag)
    while len(token_elements) > 0:
        if token_elements[-1].text == '(' or compile_element.text in ['(', '~']:
            # Handle function
            if compile_element.text == '~':
                token_element = token_elements.pop()
                compile_element = ET.Element(token_element.tag)
                if compile_element.text == '(':
                    compile_expression(token_elements.pop(), token_elements)
                    # Handle close parentheses
                    token_element = token_elements.pop()
                else:
                    if token_element.text in subroutine_table:
                        segment = subroutine_table.get(token_element.text).get("kind")
                        index = str(subroutine_table.get(token_element.text).get("#"))
                        curr_vm_file.write("push " + segment + " " + index + "\n")
                    elif token_element.text in class_table:
                        segment = class_table.get(token_element.text).get("kind")
                        if segment == "field":
                            segment = "this"
                        index = str(class_table.get(token_element.text).get("#"))
                        curr_vm_file.write("push " + segment + " " + index + "\n")
                return
            elif compile_element.text == '(':
                token_element = token_elements.pop()
                compile_expression(compile_element, token_elements)
            else:
                token_element = token_elements.pop()
                compile_expression_list(token_elements)
            # Handle close parentheses
            token_element = token_elements.pop()
            return
        elif token_elements[-1].text == '[':
            # Handle array
            token_element = token_elements.pop()
            compile_expression(token_elements.pop(), token_elements)
            # Handle close array
            token_element = token_elements.pop()
            return
        elif compile_element.text == '~':
            compile_element = token_elements.pop()
            compile_term(compile_element, token_elements)
        elif token_elements[-1].tag == "symbol" and not token_elements[-1].text == '.':
            # Bubble up close to previous element
            return
        else:
            token_element = token_elements.pop()
            if token_element.text in subroutine_table:
                segment = subroutine_table.get(token_element.text).get("kind")
                index = str(subroutine_table.get(token_element.text).get("#"))
                curr_vm_file.write("push " + segment + " " + index + "\n")
            elif token_element.text in class_table:
                segment = class_table.get(token_element.text).get("kind")
                if segment == "field":
                    segment = "this"
                index = str(class_table.get(token_element.text).get("#"))
                curr_vm_file.write("push " + segment + " " + index + "\n")
    raise Exception("Compilation Error: End of tokens during compile_term")

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

if __name__ == "__main__":
    if (len(sys.argv) == 2):
        if (sys.argv[1].endswith(".jack")):
            print("Translating Jack file: " + sys.argv[1])
        else:
            print("Translating Jack files for directory: " + sys.argv[1])
    else:
        print("Translating all Jack files in current directory")
    main()