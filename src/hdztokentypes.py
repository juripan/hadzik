from enum import Enum, auto
#TODO: merge this with comptypes file, maybe add more specific tuples like (comparisons, math_operations, etc.)

class TokenType(Enum):
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_CURLY = auto()
    RIGHT_CURLY = auto()
    
    COMMA = auto()
    ENDLINE = auto()

    EXIT = auto()
    PRINT = auto()

    LET = auto()
    BOOL_DEF = auto()

    IF = auto()
    ELIF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    FOR = auto()
    BREAK = auto()

    IDENT = auto()
    CHAR_LIT = auto()
    INT_LIT = auto()
    TRUE = auto()
    FALSE = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQUALS = auto()

    IS_EQUAL = auto()
    IS_NOT_EQUAL = auto()
    LARGER_THAN = auto()
    LESS_THAN = auto()
    LARGER_THAN_OR_EQ = auto()
    LESS_THAN_OR_EQ = auto()

    INCREMENT = auto()
    DECREMENT = auto()

    AND = auto()
    OR = auto()
    NOT = auto()

# strings of tokens must be what is used in the hadzik syntax
KEYWORD_TO_TOKEN_TYPE: dict[str, TokenType] = {
    "vychod": TokenType.EXIT,
    "hutor": TokenType.PRINT,

    "naj": TokenType.LET,
    "bul": TokenType.BOOL_DEF,

    "kec": TokenType.IF,
    "ikec": TokenType.ELIF,
    "inac": TokenType.ELSE,
    "kim": TokenType.WHILE,
    "zrob": TokenType.DO,
    "furt": TokenType.FOR,
    "konec": TokenType.BREAK,

    "pravda": TokenType.TRUE,
    "klamstvo": TokenType.FALSE,

    "aj": TokenType.AND,
    "abo": TokenType.OR,
    "ne": TokenType.NOT,
}

assert len(KEYWORD_TO_TOKEN_TYPE) == 16, "exhaustive keyword matching in KEYWORD_TO_TOKEN_TYPE"

COMPARISONS: tuple[TokenType, ...] = (TokenType.IS_EQUAL, TokenType.IS_NOT_EQUAL, TokenType.LARGER_THAN, TokenType.LESS_THAN, TokenType.LARGER_THAN_OR_EQ, TokenType.LESS_THAN_OR_EQ)

assert len(COMPARISONS) == 6, "all comparisons should be in COMPARISONS"

def get_prec_level(token_type: TokenType) -> int | None:
    """
    returns the precedence level of the token, 
    returns None if that token doesn't have a precedence level (token isn't a binary operator or a logical operator)
    """
    if token_type == TokenType.AND or token_type == TokenType.OR:
        return 0
    elif token_type in COMPARISONS:
        return 1
    elif token_type == TokenType.PLUS or token_type == TokenType.MINUS:
        return 2
    elif token_type == TokenType.STAR or token_type == TokenType.SLASH or token_type == TokenType.PERCENT:
        return 3
    else:
        return None
