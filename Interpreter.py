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
        ('INT_VAR',     r'[a-zA-Z_][a-zA-Z_0-9]*\s'),                   # Integer variable (lookahead for assignment and operations)
        ('STR_VAR',     r'[a-zA-Z_][a-zA-Z_0-9]*\s'),                   # String variable (lookahead for assignment and addition)
        ('ASSIGN',      r'(?<=\s)\=(?=\s)'),                            # Assignment operator
        ('PLUS_ASSIGN', r'(?<=\s)\+=(?=\s)'),                           # Addition assignment operator
        ('MINUS_ASSIGN',r'(?<=\s)-=(?=\s)'),                            # Subtraction assignment operator
        ('MULT_ASSIGN', r'(?<=\s)\*=(?=\s)'),                           # Multiplication assignment operator


        # -----------------  NEW TOKENS ----------------------- 
        ('DIV_ASSIGN', r'(?<=\s)\\=(?=\s)'),                            # Division assignment operator
        #todo for loop heeeelpp
        #todo print statements
        # -----------------------------------------------------


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

        for token in it:
            if token[0] in ['INT_VAR', 'STR_VAR']:
                var_name = token[1]
                next(it)  # skip the next token. We will deal with the Str or Int value later
                op_token = next(it)[1]  # Get the operator
                value_token = next(it)  # Get the value token
                semicolon = next(it)[1]  # Ensure semicolon

                if value_token[0] == 'NUMBER':
                    value = int(value_token[1])
                elif value_token[0] == 'STRING':
                    value = value_token[1][1:-1]  # getting rid of ""
                else: 
                    '''
                    if it's not a numebr or string, then it's a variable, 
                    then it's one of INT_VAR_VAL or STR_VAR_VAL or ASS_VAL
                    so let's get the value of that variable. 
                    '''
                    value = self.variables[value_token[1]]
                    if value is None:
                        print(f"Undefined variable '{value_token[1]}' on line {self.line_number}")
                        sys.exit()

                try: # for capturing the error where we add an int value to a string variable or vice versa
                    if op_token == '=':
                        self.variables[var_name] = value
                    elif op_token == '+=':
                        self.variables[var_name] += value
                    elif op_token == '-=':
                        self.variables[var_name] -= value
                    elif op_token == '*=':
                        self.variables[var_name] *= value
                except Exception as e:
                    print(f"Error in line: {self.line_number}")
                    sys.exit()

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
    filename = "test1.zpm"

    interpreter = Interpreter(filename);
    interpreter.run()
    # if there is no error in the .zpm file, the next line will get printed at the end
    print(interpreter.variables)

