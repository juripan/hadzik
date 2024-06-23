program -> [stmt]*

[stmt] -> {
    vychod([expr])
    naj ident = [expr]
}

[expr] -> int | ident
