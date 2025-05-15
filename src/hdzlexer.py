import hdztokentypes as tt
from hdzerrors import ErrorHandler
from comptypes import Token

class Tokenizer(ErrorHandler):
    curr_char: str | None = None
    tokens: list[Token] = []
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
    def is_valid_keyword(char: str) -> bool:
        """
        used for checking the remaining character in an identifier / keyword
        """
        return char.isalpha() or char.isdigit() or char == "_"
    
    def advance(self):
        """
        changes the current char to the next one and increments the index and the column number
        """
        if self.curr_char is not None and self.curr_char == "\n":
            self.line_number += 1
            self.column_number = -1
        self.index += 1
        self.column_number += 1
        self.curr_char = self.file_content[self.index] if self.index < len(self.file_content) else None

    def look_ahead(self, step: int = 1) -> str | None:
        """
        looks ahead step characters from the current character
        """
        return self.file_content[self.index + step] if self.index + step < len(self.file_content) else None


    def lex_number(self):
        """
        makes numbers, ints only for now
        """
        assert self.curr_char is not None, "current char shouldn't be None here"
        buffer = self.curr_char
        self.advance()
        while self.curr_char is not None and self.curr_char.isnumeric():
            buffer += self.curr_char
            self.advance()
        type_of_number = tt.INT_LIT  # if "." not in buffer else tt.floating_number
        self.tokens.append(Token(type=type_of_number, value=buffer, line=self.line_number, col=self.column_number))

    def lex_keyword(self):
        """
        makes potential keyword / identifier
        """
        assert self.curr_char is not None, "current char is a char"
        buffer: str = self.curr_char
        self.advance()
        while self.curr_char is not None and self.is_valid_keyword(self.curr_char):
            buffer += self.curr_char
            self.advance()
        self.tokens.append(self.search_for_keyword(buffer))

    def escape_char(self) -> int:
        if self.curr_char is None:
            #TODO: make the raise error be capable of accepting the line and col number without the dummy Token
            self.raise_error("Syntax", "expected a character after \\ escape", Token(tt.NEWLINE, self.line_number, self.column_number))
        assert self.curr_char is not None, "char shouldn't be None here"
        if self.curr_char == "n":
            ascii_value = 10 # ascii code for newline
        elif self.curr_char == "t":
            ascii_value = 9
        elif self.curr_char == "0":
            ascii_value = 0
        else:
            ascii_value = ord(self.curr_char)
        return ascii_value


    def lex_char(self):
        """
        makes a character literal
        """
        self.advance()
        if self.curr_char == "\\":
            self.advance()
            ascii_value = str(self.escape_char())
        elif self.curr_char is not None:
            ascii_value = str(ord(self.curr_char))
        else:
            self.raise_error("Syntax", "unclosed `'`", Token(tt.NEWLINE, self.line_number, self.column_number))
        self.tokens.append(Token(type=tt.CHAR_LIT, value=ascii_value, line=self.line_number, col=self.column_number)) # type: ignore (never unbound since else catches it)
        self.advance()
        if self.curr_char is None or self.curr_char != "'":
            self.raise_error("Syntax", "expected \"'\"", Token(tt.NEWLINE, self.line_number, self.column_number))
        self.advance()

    def lex_string(self):
        """
        makes a string literal
        """
        start_line_number, start_column_number = self.line_number, self.column_number
        self.advance()
        string: list[str] = []
        while self.curr_char != '"':
            if self.curr_char == "\\":
                self.advance()
                string.append(str(self.escape_char()))
            elif self.curr_char is not None:
                string.append(str(ord(self.curr_char)))
            else:
                self.raise_error("Syntax", "unclosed `\"` started here", Token(tt.NEWLINE, start_line_number, start_column_number))
            self.advance()
        #TODO: find a better solution to this
        string.append(str(len(string))) # passes a string length as the last number
        self.tokens.append(Token(type=tt.STR_LIT, value=",".join(string), line=self.line_number, col=self.column_number))
        self.advance()

    def tokenize(self):
        while self.curr_char is not None:
            if self.curr_char.isalpha() or self.curr_char == "_": # makes keywords, if not a keyword makes an identifier
                self.lex_keyword()
            elif self.curr_char.isnumeric():
                self.lex_number()
            elif self.curr_char == "'":
                self.lex_char()
            elif self.curr_char == '"':
                self.lex_string()
            elif self.curr_char == "=" and self.look_ahead() == "=":
                self.tokens.append(Token(type=tt.IS_EQUAL, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif self.curr_char == "!" and self.look_ahead() == "=":
                self.tokens.append(Token(type=tt.IS_NOT_EQUAL, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif self.curr_char == ">" and self.look_ahead() == "=":
                self.tokens.append(Token(type=tt.LARGER_THAN_OR_EQ, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif self.curr_char == "<" and self.look_ahead() == "=":
                self.tokens.append(Token(type=tt.LESS_THAN_OR_EQ, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif self.curr_char == "+" and self.look_ahead() == "+":
                self.tokens.append(Token(type=tt.INCREMENT, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif self.curr_char == "-" and self.look_ahead() == "-":
                self.tokens.append(Token(type=tt.DECREMENT, line=self.line_number, col=self.column_number))
                self.advance()
                self.advance()
            elif self.curr_char == "/" and self.look_ahead() == "/":
                self.advance()
                while self.curr_char not in ("\n", None):
                    self.advance()
            elif self.curr_char == "/" and self.look_ahead() == "*":
                cache = self.line_number, self.column_number
                self.advance()
                self.advance()
                while self.curr_char not in ("*", None) or self.look_ahead() not in ("/", None):
                    self.advance()
                self.advance()
                self.advance()
                if self.curr_char is None:
                    self.raise_error("Syntax", "unclosed multiline comment", Token(tt.NEWLINE, *cache))
            elif self.curr_char == "\n":
                self.tokens.append(Token(type=tt.NEWLINE, line=self.line_number, col=self.column_number))
                self.advance()
            elif self.curr_char == " ":
                self.advance()
            elif self.curr_char == "(":
                self.advance()
                self.tokens.append(Token(type=tt.LEFT_PAREN, line=self.line_number, col=self.column_number))
            elif self.curr_char == ")":
                self.advance()
                self.tokens.append(Token(type=tt.RIGHT_PAREN, line=self.line_number, col=self.column_number))
            elif self.curr_char == "{":
                self.advance()
                self.tokens.append(Token(type=tt.LEFT_CURLY, line=self.line_number, col=self.column_number))
            elif self.curr_char == "}":
                self.advance()
                self.tokens.append(Token(type=tt.RIGHT_CURLY, line=self.line_number, col=self.column_number))
            elif self.curr_char == ",":
                self.advance()
                self.tokens.append(Token(type=tt.COMMA, line=self.line_number, col=self.column_number))
            elif self.curr_char == "=":
                self.advance()
                self.tokens.append(Token(type=tt.EQUALS, line=self.line_number, col=self.column_number))
            elif self.curr_char == ">":
                self.advance()
                self.tokens.append(Token(type=tt.LARGER_THAN, line=self.line_number, col=self.column_number))
            elif self.curr_char == "<":
                self.advance()
                self.tokens.append(Token(type=tt.LESS_THAN, line=self.line_number, col=self.column_number))
            elif self.curr_char == "+":
                self.advance()
                self.tokens.append(Token(type=tt.PLUS, line=self.line_number, col=self.column_number))
            elif self.curr_char == "-":
                self.advance()
                self.tokens.append(Token(type=tt.MINUS, line=self.line_number, col=self.column_number))
            elif self.curr_char == "*":
                self.advance()
                self.tokens.append(Token(type=tt.STAR, line=self.line_number, col=self.column_number))
            elif self.curr_char == "/":
                self.advance()
                self.tokens.append(Token(type=tt.SLASH, line=self.line_number, col=self.column_number))
            elif self.curr_char == "%":
                self.advance()
                self.tokens.append(Token(type=tt.PERCENT, line=self.line_number, col=self.column_number))
            else:
                self.raise_error("Syntax", "char not included in the lexer", Token(tt.NEWLINE, self.line_number, self.column_number))
        return self.tokens
