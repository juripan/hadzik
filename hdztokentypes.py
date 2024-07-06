left_paren = "left_paren"
right_paren = "right_paren"
left_curly = "left_curly"
right_curly = "right_curly"

end_line = "end_ln"

exit_ = "vychod" # names of keywords must be what is used in the hadzik syntax
if_ = "kec"
elif_ = "ikec"
else_ = "inac"
let = "naj"

identifier = "ident"
integer = "int"
floating_number = "float"

plus = "+"
minus = "-"
star = "*"
slash = "/"
equals = "="

is_equal = "=="
is_not_equal = "!="
larger_than = ">"
less_than = "<"

all_token_types = (
    left_paren, right_paren, left_curly, right_curly,
    end_line, 
    exit_, let, if_, elif_, else_,
    identifier, integer, floating_number,
    plus, minus, star, slash, equals, 
    is_equal, is_not_equal, larger_than, less_than,
)

def get_prec_level(token_type: str) -> int | None:
    """
    returns the precedence level of the token, 
    returns None if that token doesn't have a precedence level (token isn't a binary operator)
    """
    if token_type in (is_equal, is_not_equal, larger_than, less_than):
        return 0
    elif token_type == plus or token_type == minus:
        return 1
    elif token_type == star or token_type == slash:
        return 2
    else:
        return None
