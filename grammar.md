[Program] -> [Stmt | *\n*]* <- new line for accurate error throwing during code generation

[Stmt] -> {
    vychod([Expr])
    hutor([Expr] | [Txt]) TODO rework this
    [IdentDef]
    [IdentAssign]
    [Scope]
    kec ([Expr]) [Scope] [IfPred]
    kim ([Expr]) [Scope]
    zrob [Scope] kim ([Expr])
    furt ([IdentDef], [CompExpr], [IdentAssign])[Scope]
    konec <- only inside a loop
}

[IdentDef] -> {
    naj ident = [Term] | [BinExpr]
    bul ident = [Term] | [LogicExpr]
}

[IdentAssign] -> {
    ident = [Txt]
    ident = [Expr]
    ident++
    ident--
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
    [LogicExpr]
}

[BinExpr] -> {
    [Expr] * [Expr] prec = 3
    [Expr] / [Expr] prec = 3
    [Expr] % [Expr] prec = 3
    [Expr] + [Expr] prec = 2
    [Expr] - [Expr] prec = 2
}

[LogicExpr] -> {
    [Expr] == [Expr] prec = 1
    [Expr] != [Expr] prec = 1
    [Expr] > [Expr] prec = 1
    [Expr] < [Expr] prec = 1
    [Expr] <= [Expr] prec = 1
    [Expr] >= [Expr] prec = 1
    [Expr] aj [Expr] prec = 0
    [Expr] abo [Expr] prec = 0
}

[Term] -> {
    int
    char
    bool
    ident
    ([Expr])
    ne [Term]
}
