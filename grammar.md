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
    naj ident = [Expr]
    bul ident = [BoolTerm]
}

[BoolTerm] ->{
    pravda
    klamstvo
    [CompExpr]
    [LogicExpr]
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
}

[BinExpr] -> {
    [Expr] * [Expr] prec = 3
    [Expr] / [Expr] prec = 3
    [Expr] % [Expr] prec = 3
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

[Txt] -> {
    char
    ident
}