import hdztokentypes as tt
from hdzerrors import ErrorHandler
from comptypes import Token

def is_valid_keyword_content(char: str) -> bool:
    """
    used for checking the remaining character in an identifier / keyword
    """
    return char.isalpha() or char.isdigit() or char == "_"


class Tokenizer(ErrorHandler):
    def __init__(self, file_content: str) -> None:
        super().__init__(file_content)
        self.current_char: str | None = None
        self.index: int = -1
        self.advance()

    def search_for_keyword(self, potential_keyword: str) -> Token:
        """
        sees if a keyword is in the tokens list, otherwise makes an identifier
        """
        if potential_keyword in tt.all_token_types:
            return Token(type=potential_keyword, value=None, line=self.line_number, col=self.column_number)
        else:
            return Token(type=tt.identifier, value=potential_keyword, line=self.line_number, col=self.column_number)
    
    def advance(self):
        """
        changes the current char to the next one and increments the index and the column number
        """
        if self.current_char is not None and self.current_char == "\n":
            self.line_number += 1
            self.column_number = -1
        self.index += 1
        self.column_number += 1
        self.current_char = self.file_content[self.index] if self.index < len(self.file_content) else None

    def look_ahead(self,step: int = 1) -> str | None:
        """
        looks ahead step characters from the current character
        """
        return self.file_content[self.index + step] if self.index + step < len(self.file_content) else None

    def tokenize(self):
        tokens: list[Token] = []
        while self.current_char is not None:
            char: str = self.current_char
            buffer = ""

            if char.isalpha() or char == "_": #makes keywords, if not a keyword makes an identifier
                buffer += char
                self.advance()
                while is_valid_keyword_content(self.current_char):
                    buffer += self.current_char
                    self.advance()
                tokens.append(self.search_for_keyword(buffer))
                buffer = ""
            
            elif char.isnumeric(): #makes numbers, ints only for now
                buffer += char
                self.advance()
                while self.current_char.isnumeric():  # or self.current_char == ".":
                    buffer += self.current_char
                    self.advance()
                type_of_number = tt.int_lit  # if "." not in buffer else tt.floating_number
                tokens.append(Token(type=type_of_number, value=buffer, line=self.line_number, col=self.column_number))
                buffer = ""
            
            elif char == "'":
                self.advance()
                if self.current_char == "\\":
                    self.advance()
                    if self.current_char == "n":
                        ascii_value = 10 # ascii code for newline
                    elif self.current_char == "t":
                        ascii_value = 9
                    else:
                        ascii_value = ord(self.current_char)    
                else:
                    ascii_value = ord(self.current_char)
                tokens.append(Token(type=tt.char_lit, value=str(ascii_value), line=self.line_number, col=self.column_number))
                self.advance()
                if self.current_char is None or self.current_char != "'":
                    self.raise_error("Syntax", "expected \"'\"")
                self.advance()
            
            elif char == "=" and self.look_ahead() == "=":
                self.advance()
                self.advance()
                tokens.append(Token(type=tt.is_equal, line=self.line_number, col=self.column_number))
            elif char == "!" and self.look_ahead() == "=":
                self.advance()
                self.advance()
                tokens.append(Token(type=tt.is_not_equal, line=self.line_number, col=self.column_number))
            elif char == ">" and self.look_ahead() == "=":
                self.advance()
                self.advance()
                tokens.append(Token(type=tt.larger_than_or_eq, line=self.line_number, col=self.column_number))
            elif char == "<" and self.look_ahead() == "=":
                self.advance()
                self.advance()
                tokens.append(Token(type=tt.less_than_or_eq, line=self.line_number, col=self.column_number))
            elif char == "+" and self.look_ahead() == "+":
                self.advance()
                self.advance()
                tokens.append(Token(type=tt.increment, line=self.line_number, col=self.column_number))
            elif char == "-" and self.look_ahead() == "-":
                self.advance()
                self.advance()
                tokens.append(Token(type=tt.decrement, line=self.line_number, col=self.column_number))
            elif char == "/" and self.look_ahead() == "/":
                self.advance()
                while self.current_char not in ("\n", None):
                    self.advance()
            elif char == "/" and self.look_ahead() == "*":
                cache = self.line_number, self.column_number
                self.advance()
                self.advance()
                while self.current_char not in ("*", None) or self.look_ahead() not in ("/", None):
                    self.advance()
                self.advance()
                self.advance()
                if self.current_char is None:
                    self.line_number, self.column_number = cache
                    self.raise_error("Syntax", "unclosed multiline comment")
            elif char == "\n":
                self.advance()
                tokens.append(Token(type=tt.end_line, line=self.line_number, col=self.column_number))
            elif char == " ":
                self.advance()
            elif char == "(":
                self.advance()
                tokens.append(Token(type=tt.left_paren, line=self.line_number, col=self.column_number))
            elif char == ")":
                self.advance()
                tokens.append(Token(type=tt.right_paren, line=self.line_number, col=self.column_number))
            elif char == "{":
                self.advance()
                tokens.append(Token(type=tt.left_curly, line=self.line_number, col=self.column_number))
            elif char == "}":
                self.advance()
                tokens.append(Token(type=tt.right_curly, line=self.line_number, col=self.column_number))
            elif char == ",":
                self.advance()
                tokens.append(Token(type=tt.dash, line=self.line_number, col=self.column_number))
            elif char == "=":
                self.advance()
                tokens.append(Token(type=tt.equals, line=self.line_number, col=self.column_number))
            elif char == ">":
                self.advance()
                tokens.append(Token(type=tt.larger_than, line=self.line_number, col=self.column_number))
            elif char == "<":
                self.advance()
                tokens.append(Token(type=tt.less_than, line=self.line_number, col=self.column_number))
            elif char == "+":
                self.advance()
                tokens.append(Token(type=tt.plus, line=self.line_number, col=self.column_number))
            elif char == "-":
                self.advance()
                tokens.append(Token(type=tt.minus, line=self.line_number, col=self.column_number))
            elif char == "*":
                self.advance()
                tokens.append(Token(type=tt.star, line=self.line_number, col=self.column_number))
            elif char == "/":
                self.advance()
                tokens.append(Token(type=tt.slash, line=self.line_number, col=self.column_number))
            elif char == "%":
                self.advance()
                tokens.append(Token(type=tt.percent, line=self.line_number, col=self.column_number))
            else:
                self.raise_error("Syntax", "char not included in the lexer")
        return tokens
