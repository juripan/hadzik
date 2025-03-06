
token_type = int


def auto_generator():
    num: token_type = 0
    while num < 50:
        yield num
        num += 1

auto = auto_generator()

LEFT_PAREN = next(auto)
RIGHT_PAREN = next(auto)
LEFT_CURLY = next(auto)
RIGHT_CURLY = next(auto)

COMMA = next(auto)
ENDLINE = next(auto)

EXIT = next(auto)
PRINT = next(auto)

LET = next(auto)
BOOL_DEF = next(auto)

IF = next(auto)
ELIF = next(auto)
ELSE = next(auto)
WHILE = next(auto)
DO = next(auto)
FOR = next(auto)
BREAK = next(auto)

IDENT = next(auto)
CHAR_LIT = next(auto)
INT_LIT = next(auto)
TRUE = next(auto)
FALSE = next(auto)

PLUS = next(auto)
MINUS = next(auto)
STAR = next(auto)
SLASH = next(auto)
PERCENT = next(auto)
EQUALS = next(auto)

IS_EQUAL = next(auto)
IS_NOT_EQUAL = next(auto)
LARGER_THAN = next(auto)
LESS_THAN = next(auto)
LARGER_THAN_OR_EQ = next(auto)
LESS_THAN_OR_EQ = next(auto)

INCREMENT = next(auto)
DECREMENT = next(auto)

AND = next(auto)
OR = next(auto)
NOT = next(auto)

# strings of tokens must be what is used in the hadzik syntax
KEYWORD_TO_TOKEN_TYPE: dict[str, token_type] = {
    "vychod": EXIT,
    "hutor": PRINT,

    "naj": LET,
    "bul": BOOL_DEF,

    "kec": IF,
    "ikec": ELIF,
    "inac": ELSE,
    "kim": WHILE,
    "zrob": DO,
    "furt": FOR,
    "konec": BREAK,

    "pravda": TRUE,
    "klamstvo": FALSE,

    "aj": AND,
    "abo": OR,
    "ne": NOT,
}

assert len(KEYWORD_TO_TOKEN_TYPE) == 16, "exhaustive keyword matching in KEYWORD_TO_TOKEN_TYPE"

COMPARISONS: tuple[token_type, ...] = (IS_EQUAL, IS_NOT_EQUAL, LARGER_THAN, LESS_THAN, LARGER_THAN_OR_EQ, LESS_THAN_OR_EQ)


def get_prec_level(tt: token_type) -> int | None:
    """
    returns the precedence level of the token, 
    returns None if that token doesn't have a precedence level (token isn't a binary operator or a logical operator)
    """
    if tt == AND or tt == OR:
        return 0
    elif tt in COMPARISONS:
        return 1
    elif tt == PLUS or tt == MINUS:
        return 2
    elif tt == STAR or tt == SLASH or tt == PERCENT:
        return 3
    else:
        return None
