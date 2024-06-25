[Program] -> [Stmt]*

[Stmt] -> {
    vychod([Expr])
    naj ident = [Expr]
}

[Expr] -> {
    [Term]
    [BinExpr]
}

[BinExpr] -> {
    [Expr] * [Expr] prec = 1
    [Expr] / [Expr] prec = 1
    [Expr] + [Expr] prec = 0
    [Expr] - [Expr] prec = 0
}

[Term] -> {
    int
    ident
    ([Expr])
}