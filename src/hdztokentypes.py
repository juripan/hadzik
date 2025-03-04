#TODO: merge this with comptypes file, maybe add more specific tuples like (comparisons, math_operations, etc.)

token_type = int

# used for enum values
_num: token_type = -1

def auto() -> token_type:
    global _num
    _num += 1
    return _num


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

assert len(COMPARISONS) == 6, "all comparisons should be in COMPARISONS"

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
