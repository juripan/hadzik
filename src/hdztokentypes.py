token_type = str

LEFT_PAREN = "("
RIGHT_PAREN = ")"
LEFT_CURLY = "{"
RIGHT_CURLY = "}"

COMMA = ","
NEWLINE = "newline"

EXIT = "exit"
PRINT = "hutor"

INFER_DEF = "naj"
INT_DEF = "cif"
BOOL_DEF = "bul"
CHAR_DEF = "znak"

IF = "kec"
ELIF = "ikec"
ELSE = "inac"
WHILE = "kim"
DO = "zrob"
FOR = "furt" # TODO: reuse this for const keyword
FOR_EVERY = "sicke" # TODO: implement new for loops
IN = "zos" # TODO: implement range
BREAK = "konec"

IDENT = "indentifier"
CHAR_LIT = "char"
INT_LIT = "int"
TRUE = "pravda"
FALSE = "klamstvo"

PLUS = "+"
MINUS = "-"
STAR = "*"
SLASH = "/"
PERCENT = "%"
EQUALS = "="

IS_EQUAL = "=="
IS_NOT_EQUAL = "!="
LARGER_THAN = ">"
LESS_THAN = "<"
LARGER_THAN_OR_EQ = ">="
LESS_THAN_OR_EQ = "<="

INCREMENT = "++"
DECREMENT = "--"

AND = "aj"
OR = "abo"
NOT = "ne"

# strings of tokens must be what is used in the hadzik syntax
KEYWORD_TO_TOKEN_TYPE: dict[str, token_type] = {
    "vychod": EXIT,
    "hutor": PRINT,

    "naj": INFER_DEF,
    "cif": INT_DEF,
    "bul": BOOL_DEF,
    "znak": CHAR_DEF,

    "kec": IF,
    "ikec": ELIF,
    "inac": ELSE,
    "kim": WHILE,
    "zrob": DO,
    "furt": FOR,
    "sicke": FOR_EVERY,
    "zos": IN,
    "konec": BREAK,

    "pravda": TRUE,
    "klamstvo": FALSE,

    "aj": AND,
    "abo": OR,
    "ne": NOT,
}

COMPARISONS: tuple[token_type, ...] = (
    IS_EQUAL, IS_NOT_EQUAL, LARGER_THAN, LESS_THAN, LARGER_THAN_OR_EQ, LESS_THAN_OR_EQ
)


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
