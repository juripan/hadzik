import hdztokentypes as tt
from hdzerrors import ErrorHandler
from comptypes import Token

class Tokenizer(ErrorHandler):
    current_char: str | None = None
    index: int = -1
    
    def __init__(self, file_content: str) -> None:
        super().__init__(file_content)
        self.advance() # sets the current char

    def search_for_keyword(self, potential_keyword: str) -> Token:
        """
        sees if a keyword is in the tokens list, otherwise makes an identifier
        """
        if potential_keyword in tt.KEYWORD_TO_TOKEN_TYPE:
            return Token(type=tt.KEYWORD_TO_TOKEN_TYPE[potential_keyword], value=None, line=self.line_number, col=self.column_number - len(potential_keyword))
        else:
            return Token(type=tt.IDENT, value=potential_keyword, line=self.line_number, col=self.column_number)
    
    @staticmethod
    def is_valid_keyword_content(char: str) -> bool:
        """
        used for checking the remaining character in an identifier / keyword
        """
        return char.isalpha() or char.isdigit() or char == "_"
    
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

    def look_ahead(self, step: int = 1) -> str | None:
        """
        looks ahead step characters from the current character
        """
        return self.file_content[self.index + step] if self.index + step < len(self.file_content) else None

    def lex_char(self, tokens: list[Token]):
        self.advance()
        if self.current_char == "\\":
            self.advance()
            if self.current_char == "n": # type: ignore
                ascii_value = 10 # ascii code for newline
            elif self.current_char == "t": # type: ignore
                ascii_value = 9
            elif self.current_char == "0": # type: ignore
                ascii_value = 0
            else:
                ascii_value = ord(self.current_char)    
        elif self.current_char is not None: # type: ignore
            ascii_value = ord(self.current_char)
        else:
            self.raise_error("Syntax", "unclosed \"'\"", Token(tt.NEWLINE, self.line_number, self.column_number))
        tokens.append(Token(type=tt.CHAR_LIT, value=str(ascii_value), line=self.line_number, col=self.column_number)) # type: ignore (never unbound since else catches it)
        self.advance()
        if self.current_char is None or self.current_char != "'": # type: ignore
            self.raise_error("Syntax", "expected \"'\"", Token(tt.NEWLINE, self.line_number, self.column_number))
        self.advance()

    def tokenize(self):
        tokens: list[Token] = []
        while self.current_char is not None:
            char: str = self.current_char
            buffer = ""
            if char.isalpha() or char == "_": # makes keywords, if not a keyword makes an identifier
                buffer += char
                self.advance()
                while self.current_char is not None and self.is_valid_keyword_content(self.current_char): # type: ignore (doesn't think it can be None but definitely can)
                    buffer += self.current_char
                    self.advance()
                tokens.append(self.search_for_keyword(buffer))
                buffer = ""
            elif char.isnumeric(): # makes numbers, ints only for now
                buffer += char
                self.advance()
                while self.current_char is not None and self.current_char.isnumeric():  # type: ignore (can be definitely None)
                    buffer += self.current_char
                    self.advance()
                type_of_number = tt.INT_LIT  # if "." not in buffer else tt.floating_number
                tokens.append(Token(type=type_of_number, value=buffer, line=self.line_number, col=self.column_number))
                buffer = ""
            elif char == "'":
                self.lex_char(tokens)
            elif char == "=" and self.look_ahead() == "=":
                tokens.append(Token(type=tt.IS_EQUAL, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif char == "!" and self.look_ahead() == "=":
                tokens.append(Token(type=tt.IS_NOT_EQUAL, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif char == ">" and self.look_ahead() == "=":
                tokens.append(Token(type=tt.LARGER_THAN_OR_EQ, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif char == "<" and self.look_ahead() == "=":
                tokens.append(Token(type=tt.LESS_THAN_OR_EQ, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif char == "+" and self.look_ahead() == "+":
                tokens.append(Token(type=tt.INCREMENT, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif char == "-" and self.look_ahead() == "-":
                tokens.append(Token(type=tt.DECREMENT, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
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
                if self.current_char is None: # type: ignore
                    self.raise_error("Syntax", "unclosed multiline comment", Token(tt.NEWLINE, *cache))
            elif char == "\n":
                tokens.append(Token(type=tt.NEWLINE, line=self.line_number, col=self.column_number))
                self.advance()
            elif char == " ":
                self.advance()
            elif char == "(":
                self.advance()
                tokens.append(Token(type=tt.LEFT_PAREN, line=self.line_number, col=self.column_number))
            elif char == ")":
                self.advance()
                tokens.append(Token(type=tt.RIGHT_PAREN, line=self.line_number, col=self.column_number))
            elif char == "{":
                self.advance()
                tokens.append(Token(type=tt.LEFT_CURLY, line=self.line_number, col=self.column_number))
            elif char == "}":
                self.advance()
                tokens.append(Token(type=tt.RIGHT_CURLY, line=self.line_number, col=self.column_number))
            elif char == ",":
                self.advance()
                tokens.append(Token(type=tt.COMMA, line=self.line_number, col=self.column_number))
            elif char == "=":
                self.advance()
                tokens.append(Token(type=tt.EQUALS, line=self.line_number, col=self.column_number))
            elif char == ">":
                self.advance()
                tokens.append(Token(type=tt.LARGER_THAN, line=self.line_number, col=self.column_number))
            elif char == "<":
                self.advance()
                tokens.append(Token(type=tt.LESS_THAN, line=self.line_number, col=self.column_number))
            elif char == "+":
                self.advance()
                tokens.append(Token(type=tt.PLUS, line=self.line_number, col=self.column_number))
            elif char == "-":
                self.advance()
                tokens.append(Token(type=tt.MINUS, line=self.line_number, col=self.column_number))
            elif char == "*":
                self.advance()
                tokens.append(Token(type=tt.STAR, line=self.line_number, col=self.column_number))
            elif char == "/":
                self.advance()
                tokens.append(Token(type=tt.SLASH, line=self.line_number, col=self.column_number))
            elif char == "%":
                self.advance()
                tokens.append(Token(type=tt.PERCENT, line=self.line_number, col=self.column_number))
            else:
                self.raise_error("Syntax", "char not included in the lexer", Token(tt.NEWLINE, self.line_number, self.column_number))
        return tokens
