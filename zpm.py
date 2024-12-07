import re   # for using regular expression
import sys  # for terminating the program when error happens

''' 1- Lexical analysis: is the first phase of a compiler. 
    Its main job is to read the input source code and convert it into meaningful
    units called tokens. This is done by a component of the compiler or interpreter
    known as the lexer or lexical analyzer.The result will be a stream of tokens 
    for each line of the code. 

    2- Parsing: Once the lexical analysis is complete, the next stage is parsing. 
    The parser takes the stream of tokens produced by the lexer and builds a data
    structure known as a parse tree or syntax tree. This tree represents the 
    grammatical structure of the program.
'''

class Interpreter:

    # Class attribute for token specifications accessible to all instances
    TOKEN_SPECIFICATION = (
        ('FOR_LOOP',    r'\bFOR\b\s+\d+\s+((?:[a-zA-Z_][a-zA-Z_0-9]*\s*[\+\-\*\\]?=\s*(?:\d+|\"[^\"]*\")|PRINT\s+[a-zA-Z_][a-zA-Z_0-9]*\s*[;]?)\s*;?\s*)*\bENDFOR\b'),   # For loop (ChatGPT assisted in specifications for this)
        ('PRINT_VAR',   r'\bPRINT\s+[a-zA-Z_][a-zA-Z_0-9]*\b'),         # Print statement
        ('INT_VAR',     r'[a-zA-Z_][a-zA-Z_0-9]*\s'),                   # Integer variable (lookahead for assignment and operations)
        ('STR_VAR',     r'[a-zA-Z_][a-zA-Z_0-9]*\s'),                   # String variable (lookahead for assignment and addition)
        ('ASSIGN',      r'(?<=\s)\=(?=\s)'),                            # Assignment operator
        ('PLUS_ASSIGN', r'(?<=\s)\+=(?=\s)'),                           # Addition assignment operator
        ('MINUS_ASSIGN',r'(?<=\s)-=(?=\s)'),                            # Subtraction assignment operator
        ('MULT_ASSIGN', r'(?<=\s)\*=(?=\s)'),                           # Multiplication assignment operator
        ('DIV_ASSIGN',  r'(?<=\s)\\=(?=\s)'),                           # Division assignment operator
        ('INT_VAR_VAL', r'(?<=[\+\-\*]=)\s[a-zA-Z_][a-zA-Z_0-9]*'),     # Integer variable (lookahead for operations)
        ('STR_VAR_VAL', r'(?<=\+=)\s[a-zA-Z_][a-zA-Z_0-9]*'),           # String variable (lookahead for addition)
        ('ASS_VAL', r'(?<=\=)\s[a-zA-Z_][a-zA-Z_0-9]*'),                # variable (lookahead for assignment)
        ('NUMBER',      r'(?<=\s)-?\d+(?=\s)'),                         # Integer literal
        ('STRING',      r'"[^"]*"'),                                    # String literal, handling quotes
        ('SEMICOLON',   r'(?<=\s);'),                                   # Statement terminator
        ('WS',          r'\s+'),                                        # Whitespace
        ('NEWLN',       r'\n')
    )

    def __init__(self, file_name):
        self.file_name = file_name
        self.variables = {}
        self.line_number = 0

    def lexical_analysis(self, line):
        """
        This function uses regular expression for tokenizing. 
        There are other tools and algorithms for tokenizing such as:
        1- tool: FLexer Generators (e.g., Lex, Flex)
        2- Maximal Munch (or Longest Match) Principle
        """
        tokens = []

        # looping through all patterns
        for tok_type, tok_regex in self.TOKEN_SPECIFICATION:
            # compiling a string pattern into its actual pattern matching
            regex = re.compile(tok_regex)
            # looking for a match
            match = regex.search(line)

            if match and tok_type != 'WS' and tok_type != 'NEWLN':  # Skip whitespace and newLine
                    token = (tok_type, match.group(0).strip())  # getting the match from the line
                    tokens.append(token)
                    
        return tokens


    
                

    def parse(self, tokens):
        '''
        Usually in parsisng phase, the tokens are checked and then a data structure (usually a tree)
        will be constructed from tokens that will be send to another method, and that method actually
        translate and runs the tokens. HERE, we are combining the parsing with also executing the tokens. 
        Just to keep things simpler.
        '''
        it = iter(tokens)
        try: 
            for token in it:
                if token[0] == 'PRINT_VAR':
                    # skip over token name etc to variable
                    next(it)
                    next(it)
                    # get part that is just the variable name
                    variable_name = re.sub(r"^PRINT\s+", "", token[1])

                    # check to see if the variable actually exists
                    if variable_name in self.variables:
                        # if it does, grab it
                        variable_value = self.variables[variable_name]
                        # have to check if it is a string or not, as strings are printed with quotes around them
                        if type(variable_value) == str:
                            print(f'{variable_name} = "{variable_value}"')
                        else:
                            print(f'{variable_name} = {variable_value}')

                
                if token[0] in ['INT_VAR', 'STR_VAR'] and not (token[0] == 'PRINT'):
                    variable_name = token[1]
                    try:
                        next(it)  # skip the next token. We will deal with the Str or Int value later
                        op_token = next(it)[1]  # Get the operator
                        value_token = next(it)  # Get the value token
                        semicolon = next(it)[1]  # Ensure semicolon

                        if value_token[0] == 'NUMBER':
                            variable_value = int(value_token[1])
                        elif value_token[0] == 'STRING':
                            variable_value = value_token[1][1:-1]  # getting rid of ""
                        else: 
                            '''
                            if it's not a number or string, then it's a variable, 
                            then it's one of INT_VAR_VAL or STR_VAR_VAL or ASS_VAL
                            so let's get the value of that variable. 
                            '''
                            if value_token[1] not in self.variables:
                                print(f"Undefined variable '{value_token[1]}' on line {self.line_number}")
                                sys.exit(1)
                                variable_value = self.variables[value_token[1]]
                            

                        try: # for capturing the error where we add an int value to a string variable or vice versa
                            if op_token == '=':
                                self.variables[variable_name] = variable_value
                            elif op_token == '+=':
                                if variable_name not in self.variables:
                                    # Initialize with empty string or 0 (credits to ChatGPT for the idea of doing this and help implementing it)
                                    self.variables[variable_name] = type(variable_value)()
                                self.variables[variable_name] += variable_value # the actual computation for addition
                            elif op_token == '-=':
                                if variable_name not in self.variables:
                                    self.variables[variable_name] = 0 # giving default value of zero (ChatGPT idea)
                                self.variables[variable_name] -= variable_value # doing the subtraction
                            elif op_token == '*=':
                                if variable_name not in self.variables:
                                    self.variables[variable_name] = 0
                                self.variables[variable_name] *= variable_value # doing the multiplication
                            elif op_token == '\\=':
                                if variable_name not in self.variables:
                                    self.variables[variable_name] = 0
                                # check for divide by zero 
                                if variable_value == 0:
                                    print(f"Divide by zero on line {self.line_number}")
                                    sys.exit(1)
                                # need to use integer division here
                                self.variables[variable_name] //= variable_value # doing the division
                        # i.e. trying to add string to integer
                        except TypeError as e:
                            print(f"Type error in line {self.line_number}: Cannot perform operation {op_token} between these types")
                            sys.exit(1)
                        # general error by line
                        except Exception as e:
                            print(f"Error in line {self.line_number}: {str(e)}")
                            sys.exit(1)
                    # in case of incomplete statement or run out of tokens when it shouldn't have        
                    except StopIteration:
                        print(f"Incomplete statement on line {self.line_number}")
                        sys.exit(1)
        # default exception catch 
        except Exception as e:
            print(f"Error parsing line {self.line_number}: {str(e)}")
            sys.exit(1)

                
            






    def run(self, file_name = ""):
        """
        Runs the interpreter on the provided file.
        """
        if file_name == "":
            file_name = self.file_name

        self.line_number = 0

        with open(file_name, 'r') as file:
            for line in file:
                self.line_number += 1

                tokens = self.lexical_analysis(line)
                self.parse(tokens)

        

if __name__ == "__main__":
     # The second argument in sys.argv is expected to be the filename
    
    #filename = sys.argv[1]  # for getting the filename from command line
    #OR

    filename = ""

    # check argv for filename
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # print error statement and exit if the run command does not follow format
        print("Incorrect run command. Try \"python3 zpm.py [filename.zpm]\"")
        sys.exit(1)

    interpreter = Interpreter(filename);
    interpreter.run()
    # if there is no error in the .zpm file, the next line will get printed at the end
    print(interpreter.variables)

