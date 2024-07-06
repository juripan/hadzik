[Program] -> [Stmt]*

[Stmt] -> {
    vychod([Expr])
    naj ident = [Expr]
    ident = [Expr]
    [Scope]
    kec [Expr] [Scope] [IfPred]
}

[Scope] -> {[Stmt]*}

[IfPred] -> {
    ikec [Expr] [Scope] [IfPred]
    inac [Scope]
    *nothing*
}

[Expr] -> {
    [Term]
    -[Term]
    [BinExpr]
}

[BinExpr] -> {
    [Expr] * [Expr] prec = 2
    [Expr] / [Expr] prec = 2
    [Expr] + [Expr] prec = 1
    [Expr] - [Expr] prec = 1
    [Expr] == [Expr] prec = 0
    [Expr] != [Expr] prec = 0
    [Expr] > [Expr] prec = 0
    [Expr] < [Expr] prec = 0
}

[Term] -> {
    int
    ident
    ([Expr])
}