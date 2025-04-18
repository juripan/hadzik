$$
\begin{align*}
    [\text{Program}] &\to
    \begin{cases}
    [\text{Stmt}]^*\\
    \end{cases}\\

    [Stmt] &\to
    \begin{cases}
        vychod([\text{Expr}])\\
        hutor(\text{char}) \\
        [\text{IdentDef}]\\
        [\text{IdentAssign}]\\
        [\text{Scope}]\\
        kec [\text{Expr}] [\text{Scope}] [\text{IfPred}]\\
        kim [\text{Expr}] [\text{Scope}]\\
        zrob [\text{Scope}] kim [\text{Expr}]\\
        furt ([\text{IdentDef}], [\text{CompExpr}], [\text{IdentAssign}])[\text{Scope}]\\
        konec \leftarrow \text{only inside a loop}\\
        \text{newline}
    \end{cases}\\

    [\text{IdentDef}] &\to
    \begin{cases}
        cif \space \text{ident} = [\text{Expr}]\\
        bul \space \text{ident} = [\text{LogicExpr}]\\
        znak \space \text{ident} = [\text{Term}]\\
        naj \space \text{ident} = [\text{Expr}]\\
    \end{cases}\\

    [\text{IdentAssign}] &\to
    \begin{cases}
        \text{ident} = [\text{Expr}]\\
        \text{ident}++\\
        \text{ident}--\\
    \end{cases}\\

    [\text{Scope}] &\to 
    \begin{cases}
        \{[\text{Stmt}]^*\}\\
    \end{cases}\\

    [\text{IfPred}] &\to
    \begin{cases}
        ikec [\text{Expr}] [\text{Scope}] [\text{IfPred}]\\
        inac [\text{Scope}]\\
        \epsilon
    \end{cases}\\

    [\text{Expr}] &\to
    \begin{cases}
        [\text{Term}]\\
        [\text{BinExpr}]\\
        [\text{BoolExpr}]\\
    \end{cases}\\

    [\text{BinExpr}] &\to
    \begin{cases}
        [\text{Expr}] * [\text{Expr}] & \text{prec} = 3\\
        [\text{Expr}] / [\text{Expr}] & \text{prec} = 3\\
        [\text{Expr}] \% [\text{Expr}] & \text{prec} = 3\\
        [\text{Expr}] + [\text{Expr}] & \text{prec} = 2\\
        [\text{Expr}] - [\text{Expr}] & \text{prec} = 2\\
    \end{cases}\\

    [\text{BoolExpr}] &\to
    \begin{cases}
        [\text{PredExpr}]\\
        [\text{LogicExpr}]\\
    \end{cases}\\

    [\text{PredExpr}] &\to
    \begin{cases}
        [\text{Expr}] == [\text{Expr}] & \text{prec} = 1\\
        [\text{Expr}] != [\text{Expr}] & \text{prec} = 1\\
        [\text{Expr}] > [\text{Expr}] & \text{prec} = 1\\
        [\text{Expr}] < [\text{Expr}] & \text{prec} = 1\\
        [\text{Expr}] <= [\text{Expr}] & \text{prec} = 1\\
        [\text{Expr}] >= [\text{Expr}] & \text{prec} = 1\\
    \end{cases}\\

    [\text{LogicExpr}] &\to
    \begin{cases}
        [\text{Expr}]\ aj\ [\text{Expr}] & \text{prec} = 0\\
        [\text{Expr}]\ abo\ [\text{Expr}] & \text{prec} = 0\\
    \end{cases}\\

    [\text{Term}] &\to
    \begin{cases}
        \text{int}\\
        \text{char}\\
        \text{bool}\\
        \text{ident}\\
        ([\text{Expr}])\\
        ne [\text{Term}]\\
    \end{cases}\\
\end{align*}
$$