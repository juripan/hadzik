[Program] -> [Stmt | *\n*]* <- new line for accurate error throwing during code generation

[Stmt] -> {
    vychod([Expr])
    naj ident = [Expr]
    ident = [Expr]
    [Scope]
    kec [Expr] [Scope] [IfPred]
    kim [Expr] [Scope]
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
    [Expr] * [Expr] prec = 3
    [Expr] / [Expr] prec = 3
    [Expr] + [Expr] prec = 2
    [Expr] - [Expr] prec = 2
    [CompExpr] prec = 1
    [LogicExpr] prec = 0
}

[CompExpr] -> {
    [Expr] == [Expr]
    [Expr] != [Expr]
    [Expr] > [Expr]
    [Expr] < [Expr]
    [Expr] <= [Expr]
    [Expr] >= [Expr]
}

[LogicExpr] -> {
    [Expr] aj [Expr]
    [Expr] abo [Expr]
}

[Term] -> {
    int
    ident
    ([Expr])
    ne [Term]
}