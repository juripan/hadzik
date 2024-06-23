left_paren = "left_paren"
right_paren = "right_paren"
end_line = "end_ln"

exit_ = "vychod" # names of keywords must be what is used in the hadzik syntax
let = "naj"

identifier = "ident"
integer = "int"
floating_number = "float"

plus = "+"
minus = "-"
star = "*"
slash = "/"
equals = "="

all_token_types = (
    left_paren, right_paren, end_line, 
    exit_, let, 
    identifier, integer, floating_number,
    plus, minus, star, slash
)

bin_op = (
    plus, minus, star, slash
)