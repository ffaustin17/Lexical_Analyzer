#Author: Fabrice Faustin


# this program lexically analyzes a jack file and writes the output into an xml file
# please read the Lab Tokenizer.pdf and Tokenizer_Jack_Syntax.pdf files for more context on how the lexical
# analysis, particularly what the lexical analyzer will recognize as tokens/lexemes in the input jack codes.

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# variables

comment_started = False
comment_ended = False

is_line_comment = False
is_multi_comment = False

input_file = None
output_file = None

curr_character = ''
last_character = ''

filename_no_ext = ''  #the name of the file without the extension

INPUT_FILE_EXTENSION = '.jack'
OUTPUT_FILE_EXTENSION = '.xml'

filename_no_ext = input('Enter the name of the .jack file you want to read (do not include the extension): ')


filename = filename_no_ext + INPUT_FILE_EXTENSION

#we read the .jack file
input_file = open(filename, mode='r')  

#this string will hold the content of the .jack file without the comments
content = ''

#constant lexemes. Their corresponding token is the name of the container
SYMBOLS = ['(', ')', '[', ']', '{', '}', ',', '.', ';', '=', '+', '-', '*', '/', '&', '|', '~', '<', '>', ' ']
KEYWORDS = ['class','constructor', 'method', 'function', 'int', 'boolean', 'char', 'void', 'var', 'static', 'field', 'let', 'do', 'if', 'else', 'while', 'return', 'true', 'false', 'null', 'this']

#this list will contain the xml token output of the jack code we read
token_output = []


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#analyze a given lexeme. returns the xml token equivalent 
def lex(lexeme):
    if(lexeme in SYMBOLS):
        if(lexeme == '>'):
            lexeme = '&gt;'

        if(lexeme == '<'):
            lexeme = '&lt;'
            
        return '\t<symbol> ' + lexeme + ' </symbol>\n'
    elif(lexeme in KEYWORDS):
        return '\t<keyword> ' + lexeme + ' </keyword>\n'
    elif(lexeme[0] == '"'):   #a lexeme is a string if it starts with a quotation mark. We do not need to worry about it ending with a quotation mark because the lexeme can simply not start with a quotation mark and not end with one.
        lexeme_end = len(lexeme) -1 
        lexeme = lexeme[1:lexeme_end] # we strip the lexeme of the quotation mark to only print the actual content of the string

        if(lexeme == '"'): # this means that our string is empty, we give a special xml descriptor for that
            return '\t<emptyString> ' + "None" + ' </emptyString>\n'
        else:              
            return '\t<stringConstant> ' + lexeme + ' </stringConstant>\n'
    elif(lexeme[0].isnumeric()):      #the first character of a lexeme must be an numeric for it to have a chance of being an integer constant
        if(lexeme.isnumeric()):       #if that is the case, then all of the rest of the characters must be numbers too
            return '\t<integerConstant> ' + lexeme + ' </integerConstant>\n'
        else:
            return '\t<invalid> ' + lexeme + ' </invalid>\n'
    elif(lexeme[0].isalpha() or lexeme[0] == '_'):
        for char in lexeme:
            if(char.isalpha() or char.isnumeric() or char == '_'):
                return '\t<identifier> ' + lexeme + ' </identifier>\n'
            else:
                return '\t<invalid> ' + lexeme + ' </invalid>\n'
    else:
        return '\t<invalid> ' + lexeme + ' </invalid>\n'

                
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#adds a lexeme to the token_output that will be created           
def addLexeme(token_equivalent, tokenizer_output):
    tokenizer_output.append(token_equivalent)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#remove comments from code. Return the string representing the code without comments. Note that newlines and tabs are still going to be kept
while(True):
    last_character = curr_character
    curr_character = input_file.read(1) #read one character at the time
    current_position = input_file.tell()
    next_character = input_file.read(1) #to help prevent in reading the first / character of a comment, while enabling to read the math / operator
    input_file.seek(current_position)  #returns to the current position after reading the next file

    if(curr_character != ''):   #the character is empty when we are done reading the file
        if((curr_character == '/' or curr_character == '*') and last_character == '/'): #we track for comments
            if(curr_character == '/'):
                is_line_comment = True
            else:
                is_multi_comment = True

            comment_started = True   #indicates that we are in a comment

        if(not comment_started):   #we only read characters when we are not in a comment
            if(curr_character == '/' and (next_character != '/' and next_character != '*')):
                content += curr_character

            if(curr_character != '/'):
                content += curr_character


        if(curr_character == '\n' or (curr_character == '/' and last_character == '*')):  #condition that indicates that a comment has ended
            if(comment_started and curr_character == '\n'):
                if(is_line_comment):
                    comment_ended = True
                    comment_started = False
                    is_line_comment = False
                

            if(comment_started and (curr_character == '/' and last_character == '*')):
                if(is_multi_comment):
                    comment_ended = True
                    comment_started = False
                    is_multi_comment = False

    else:
        break


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# divide the code without comments into individual lexemes. No newlines or tabs are kept
quotation = False
lexeme_str = ''
#we go through every single character in the code without the comments and construct lexemes one by one
for char in content:    
    if(char == '"'):   #to signal that we are in a string or end of a string.
        quotation = not quotation
        lexeme_str += char

    if(char != '"' and quotation == True):  #all of the characters inside a string are used for constructing the lexeme until the string ends (quotation = False)
        lexeme_str += char

    if(char != '"' and quotation == False):  #if we are not in a string, then we make sure not to read newline characters, nor tab characters. If the character is a space, this signifies the end of the lexeme, and we can analyze it
        if(char in SYMBOLS): #sometimes, two separate lexemes can be collated. This usually happens when the next character is a symbol, so we account for that and separate them       
            if(lexeme_str != ''): 
                addLexeme(lex(lexeme_str), token_output)
                lexeme_str = ''
                
            if(char != ' '): # in the case that we have already added one word/lexeme and the current character(symbol) is not a space,we need to analyze that lexeme as well
                lexeme_str += char
                addLexeme(lex(lexeme_str), token_output)
                lexeme_str = ''
                
        else:
            if(char != '\n' and char != '\t'):
                lexeme_str += char
        


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#decorators for our token ouput
token_output.insert(0, '<tokens>\n')
token_output.append('</tokens>\n')

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



#write our token output to a file


file_name = filename_no_ext + "T" + OUTPUT_FILE_EXTENSION


#write our token output to a file
output_file = open(file_name, 'w')

output_file.writelines(token_output)

#signal to the user that the xml file has been created successfully.
print()
print("The Lexical analysis is complete. You can see the result by accessing the {} file in this project's directory.".format(file_name))
print("Make sure to compare the freshly created xml file with the already existing one to see if the analysis was correct.")

#close the files
output_file.close()
input_file.close()
