import os
import sys
from xml.etree import ElementTree as ET

def main():
    if (len(sys.argv) == 2):
        for root, dirs, files in os.walk("."):
            if (sys.argv[1].endswith(".jack")):
                for name in files:
                    if name == sys.argv[1].split("/")[-1]:
                        token_xml_file_path = tokenize(os.path.join(root, name))
                        parse(token_xml_file_path)
            else:
                if (root.split("/")[-1] == (sys.argv[1])):
                    for entry in os.scandir(root):
                        if (entry.name.endswith(".jack")):
                            token_xml_file_path = tokenize(os.path.join(root, entry.name))
                            parse(token_xml_file_path)
    else:
        for entry in os.scandir():
            if (entry.name.endswith(".jack")):
                token_xml_file_path = tokenize(entry.name)
                parse(token_xml_file_path)


def tokenize(file_path: str) -> str:
    root = ET.Element("tokens")
    file_content = open(file_path, 'r').read()
    tokenize_helper(file_content, root)
    token_xml_file_path = file_path[:-5] + "T.xml"
    # ET.indent(root, space="\t", level=0)
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


def parse(token_xml_file_path: str):
    file_path = token_xml_file_path[:-5]
    token_root = ET.parse(token_xml_file_path).getroot()
    token_elements = list(token_root.iter())
    token_elements.reverse()
    compile_root = compile_class(token_elements)
    compile_xml_file_path = file_path + ".xml"
    # ET.indent(compile_root, space="\t", level=0)
    ET.ElementTree(compile_root).write(compile_xml_file_path, short_empty_elements=False)


def compile_class(token_elements: list) -> ET.Element:
    root_element = ET.Element("class")
    root_element.text = '\n'
    root_element.tail = '\n'
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.tag == "tokens":
            # Ignore since tokens tag isn't needed and class element is already setup
            continue
        elif token_element.text in ["field", "static"]:
            # ClassVarDec
            root_element.append(compile_class_var(token_element, token_elements))
        elif token_element.text in ["constructor", "function", "method"]:
            # SubroutineDec
            root_element.append(compile_subroutine(token_element, token_elements))
        else:
            # Keyword/Identifier/Symbol 
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
    return root_element


def compile_class_var(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("classVarDec")
    root_element.text = '\n'
    root_element.tail = '\n'
    compile_element = ET.Element(initial_element.tag)
    compile_element.text = initial_element.text
    compile_element.tail = '\n'
    root_element.append(compile_element)
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        # Keyword/Identifier/Symbol only
        compile_element = ET.Element(token_element.tag)
        compile_element.text = token_element.text
        compile_element.tail = '\n'
        root_element.append(compile_element)
        if token_element.text == ';':
            return root_element
    raise Exception("Compilation Error: End of tokens during compile_class_var")
        

def compile_subroutine(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("subroutineDec")
    root_element.text = '\n'
    root_element.tail = '\n'
    compile_element = ET.Element(initial_element.tag)
    compile_element.text = initial_element.text
    compile_element.tail = '\n'
    root_element.append(compile_element)
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.text == "(":
            # ParameterList
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
            root_element.append(compile_parameter_list(token_elements))
        elif token_element.text == '{':
            # SubroutineBody
            root_element.append(compile_subroutine_body(token_element, token_elements))
            return root_element
        else:
            # Keyword/Identifier/Symbol only
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
    raise Exception("Compilation Error: End of tokens during compile_subroutine")


def compile_parameter_list(token_elements: list) -> ET.Element:
    # Initial '(' for param list happens outside of element, no need for initial_element here
    root_element = ET.Element("parameterList")
    root_element.text = '\n'
    root_element.tail = '\n'
    while len(token_elements) > 0:
        if token_elements[-1].text == ')':
            # If peeked ')', return to subroutine compilation
            return root_element
        token_element = token_elements.pop()
        compile_element = ET.Element(token_element.tag)
        compile_element.text = token_element.text
        compile_element.tail = '\n'
        root_element.append(compile_element)
    raise Exception("Compilation Error: End of tokens during compile_parameter_list")


def compile_subroutine_body(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("subroutineBody")
    root_element.text = '\n'
    root_element.tail = '\n'
    # Initial '{' symbol
    compile_element = ET.Element(initial_element.tag)
    compile_element.text = initial_element.text
    compile_element.tail = '\n'
    root_element.append(compile_element)
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.text == "var":
            root_element.append(compile_var_dec(token_element, token_elements))
        elif token_element.text in ["do", "let", "while", "return", "if"]:
            # Statements
            root_element.append(compile_statements(token_element, token_elements))
        else:
            # Ending '}' symbol
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
            return root_element
    raise Exception("Compilation Error: End of tokens during compile_subroutine_body")


def compile_var_dec(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("varDec")
    root_element.text = '\n'
    root_element.tail = '\n'
    # Initial statement
    compile_element = ET.Element(initial_element.tag)
    compile_element.text = initial_element.text
    compile_element.tail = '\n'
    root_element.append(compile_element)
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        # Keyword/Identifier/Symbol only
        compile_element = ET.Element(token_element.tag)
        compile_element.text = token_element.text
        compile_element.tail = '\n'
        root_element.append(compile_element)
        if token_element.text == ';':
            return root_element
    raise Exception("Compilation Error: End of tokens during compile_var_dec")


def compile_statements(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("statements")
    root_element.text = '\n'
    root_element.tail = '\n'
    # Check initial statement
    if initial_element.text == 'do':
        root_element.append(compile_do(initial_element, token_elements))
    elif initial_element.text == 'let':
        root_element.append(compile_let(initial_element, token_elements))
    elif initial_element.text == 'while':
        root_element.append(compile_while(initial_element, token_elements))
    elif initial_element.text == 'return':
        root_element.append(compile_return(initial_element, token_elements))
    elif initial_element.text == 'if':
        root_element.append(compile_if(initial_element, token_elements))
    while len(token_elements) > 0:
        if token_elements[-1].text == 'do':
            root_element.append(compile_do(token_elements.pop(), token_elements))
        elif token_elements[-1].text == 'let':
            root_element.append(compile_let(token_elements.pop(), token_elements))
        elif token_elements[-1].text == 'while':
            root_element.append(compile_while(token_elements.pop(), token_elements))
        elif token_elements[-1].text == 'return':
            root_element.append(compile_return(token_elements.pop(), token_elements))
        elif token_elements[-1].text == 'if':
            root_element.append(compile_if(token_elements.pop(), token_elements))
        else:
            return root_element
    return root_element


def compile_do(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("doStatement")
    root_element.text = '\n'
    root_element.tail = '\n'
    # Initial statement
    compile_element = ET.Element(initial_element.tag)
    compile_element.text = initial_element.text
    compile_element.tail = '\n'
    root_element.append(compile_element)
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        compile_element = ET.Element(token_element.tag)
        compile_element.text = token_element.text
        compile_element.tail = '\n'
        root_element.append(compile_element)
        if token_element.text == '(':
            # ExpressionList
            root_element.append(compile_expression_list(token_elements))
        elif token_element.text == ';':
            # End
            return root_element
    raise Exception("Compilation Error: End of tokens during compile_do")


def compile_let(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("letStatement")
    root_element.text = '\n'
    root_element.tail = '\n'
    # Initial statement
    compile_element = ET.Element(initial_element.tag)
    compile_element.text = initial_element.text
    compile_element.tail = '\n'
    root_element.append(compile_element)
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        compile_element = ET.Element(token_element.tag)
        compile_element.text = token_element.text
        compile_element.tail = '\n'
        root_element.append(compile_element)
        if token_element.text == '=' or token_element.text == '[':
            # Expression
            root_element.append(compile_expression(token_elements.pop(), token_elements))
        elif token_element.text == ';':
            # End
            return root_element
    raise Exception("Compilation Error: End of tokens during compile_let")


def compile_while(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("whileStatement")
    root_element.text = '\n'
    root_element.tail = '\n'
    # Initial statement
    compile_element = ET.Element(initial_element.tag)
    compile_element.text = initial_element.text
    compile_element.tail = '\n'
    root_element.append(compile_element)
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        compile_element = ET.Element(token_element.tag)
        compile_element.text = token_element.text
        compile_element.tail = '\n'
        root_element.append(compile_element)
        if token_element.text == '(':
            # Expression
            root_element.append(compile_expression(token_elements.pop(), token_elements))
        elif token_element.text == '{':
            # Statements
            root_element.append(compile_statements(token_elements.pop(), token_elements))
        elif token_element.text == '}':
            return root_element
    raise Exception("Compilation Error: End of tokens during compile_while")


def compile_return(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("returnStatement")
    root_element.text = '\n'
    root_element.tail = '\n'
    # Initial statement
    compile_element = ET.Element(initial_element.tag)
    compile_element.text = initial_element.text
    compile_element.tail = '\n'
    root_element.append(compile_element)
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        if token_element.text == ';':
            # End
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
            return root_element
        else:
            # Expression
            root_element.append(compile_expression(token_element, token_elements))
    raise Exception("Compilation Error: End of tokens during compile_return")


def compile_if(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("ifStatement")
    root_element.text = '\n'
    root_element.tail = '\n'
    # Initial statement
    compile_element = ET.Element(initial_element.tag)
    compile_element.text = initial_element.text
    compile_element.tail = '\n'
    root_element.append(compile_element)
    while len(token_elements) > 0:
        token_element = token_elements.pop()
        compile_element = ET.Element(token_element.tag)
        compile_element.text = token_element.text
        compile_element.tail = '\n'
        root_element.append(compile_element)
        if token_element.text == '(':
            # Expression
            root_element.append(compile_expression(token_elements.pop(), token_elements))
        elif token_element.text == '{':
            # Statements
            root_element.append(compile_statements(token_elements.pop(), token_elements))
        elif token_element.text == '}':
            return root_element
    raise Exception("Compilation Error: End of tokens during compile_if")


def compile_expression_list(token_elements: list) -> ET.Element:
    root_element = ET.Element("expressionList")
    root_element.text = '\n'
    root_element.tail = '\n'
    while len(token_elements) > 0:
        if token_elements[-1].text == ')':            
            # If peeked ')', return to statement compilation
            return root_element
        token_element = token_elements.pop()
        if token_element.text == ',':
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
        else:
            root_element.append(compile_expression(token_element, token_elements))
    raise Exception("Compilation Error: End of tokens during compile_expression_list")


def compile_expression(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("expression")
    root_element.text = '\n'
    root_element.tail = '\n'
    root_element.append(compile_term(initial_element, token_elements))
    while len(token_elements) > 0:
        if token_elements[-1].text in [')', ']', ';', ',']:
            return root_element
        elif token_elements[-1].tag == "symbol" and token_elements[-1].text not in ['(', '[']:
            token_element = token_elements.pop()
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
        else:
            root_element.append(compile_term(token_elements.pop(), token_elements))
    return root_element


def compile_term(initial_element: ET.Element, token_elements: list) -> ET.Element:
    root_element = ET.Element("term")
    root_element.text = '\n'
    root_element.tail = '\n'
    compile_element = ET.Element(initial_element.tag)
    compile_element.text = initial_element.text
    compile_element.tail = '\n'
    root_element.append(compile_element)
    while len(token_elements) > 0:
        if token_elements[-1].text == '(' or compile_element.text in ['(', '~']:
            # Handle function
            if compile_element.text == '~':
                term_element = ET.Element("term")
                term_element.text = '\n'
                term_element.tail = '\n'
                token_element = token_elements.pop()
                compile_element = ET.Element(token_element.tag)
                compile_element.text = token_element.text
                compile_element.tail = '\n'
                term_element.append(compile_element)
                if compile_element.text == '(':
                    term_element.append(compile_expression(token_elements.pop(), token_elements))
                    # Handle close parentheses
                    token_element = token_elements.pop()
                    compile_element = ET.Element(token_element.tag)
                    compile_element.text = token_element.text
                    compile_element.tail = '\n'
                    term_element.append(compile_element)
                root_element.append(term_element)
                return root_element
            elif compile_element.text == '(':
                token_element = token_elements.pop()
                compile_element = ET.Element(token_element.tag)
                compile_element.text = token_element.text
                compile_element.tail = '\n'
                root_element.append(compile_expression(compile_element, token_elements))
            else:
                token_element = token_elements.pop()
                compile_element = ET.Element(token_element.tag)
                compile_element.text = token_element.text
                compile_element.tail = '\n'
                root_element.append(compile_element)
                root_element.append(compile_expression_list(token_elements))
            # Handle close parentheses
            token_element = token_elements.pop()
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
            return root_element
        elif token_elements[-1].text == '[':
            # Handle array
            token_element = token_elements.pop()
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
            root_element.append(compile_expression(token_elements.pop(), token_elements))
            # Handle close array
            token_element = token_elements.pop()
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
            return root_element
        elif compile_element.text == '~':
            compile_element = token_elements.pop()
            root_element.append(compile_term(compile_element, token_elements))
        elif token_elements[-1].tag == "symbol" and not token_elements[-1].text == '.':
            # Bubble up close to previous element
            return root_element
        else:
            token_element = token_elements.pop()
            compile_element = ET.Element(token_element.tag)
            compile_element.text = token_element.text
            compile_element.tail = '\n'
            root_element.append(compile_element)
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