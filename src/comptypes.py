from dataclasses import dataclass

@dataclass(slots=True)
class Token:
    type: str
    line: int
    col: int
    value: str | None = None

@dataclass(slots=True)
class NodeExpr:
    pass

@dataclass(slots=True)
class NodeTermBool:
    bool: Token

@dataclass(slots=True)
class NodeTermChar:
    char: Token

@dataclass(slots=True)
class NodeTermIdent:
    ident: Token


@dataclass(slots=True)
class NodeTermInt:
    int_lit: Token


@dataclass(slots=True)
class NodeTermParen:
    expr: NodeExpr


@dataclass(slots=True)
class NodeTermNot:
    pass


@dataclass(slots=True)
class NodeTerm:
    var: NodeTermIdent | NodeTermInt | NodeTermChar | NodeTermParen | NodeTermNot | NodeTermBool
    negative: bool = False


@dataclass(slots=True)
class NodeTermNot:
    term: NodeTerm


@dataclass(slots=True)
class NodeBinExpr:
    pass


@dataclass(slots=True)
class NodeBinExprMod:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class NodeBinExprDiv:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class NodeBinExprSub:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class NodeBinExprAdd:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class NodeBinExprMulti:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class NodeBinExprComp:
    comp_sign: Token
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class NodeBinExprLogic:
    logical_operator: Token
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class NodeBinExpr:
    var: NodeBinExprAdd | NodeBinExprMulti | NodeBinExprSub | NodeBinExprDiv | NodeBinExprMod | None

@dataclass(slots=True)
class NodeLogicExpr:
    var: NodeBinExprComp | NodeBinExprLogic

@dataclass(slots=True)
class NodeExpr:
    var: NodeTerm | NodeBinExpr | NodeLogicExpr | None


@dataclass(slots=True)
class NodeStmtExit:
    expr: NodeExpr


@dataclass(slots=True)
class NodeStmtLet:
    ident: Token
    expr: NodeExpr
    type_: Token


class NodeScope:
    pass

class NodeIfPred:
    pass


@dataclass(slots=True)
class NodeIfPredElse:
    scope: NodeScope


@dataclass(slots=True)
class NodeIfPredElif:
    expr: NodeExpr
    scope: NodeScope
    pred: NodeIfPred


@dataclass(slots=True)
class NodeIfPred:
    var: NodeIfPredElif | NodeIfPredElse


@dataclass(slots=True)
class NodeStmtIf:
    expr: NodeExpr
    scope: NodeScope
    ifpred: NodeIfPred | None


@dataclass(slots=True)
class NodeStmtReassignEq:
    ident: Token
    expr: NodeExpr


@dataclass(slots=True)
class NodeStmtReassignInc:
    ident: Token


@dataclass(slots=True)
class NodeStmtReassignDec:
    ident: Token


@dataclass(slots=True)
class NodeStmtReassign:
    var: NodeStmtReassignEq | NodeStmtReassignInc | NodeStmtReassignDec


@dataclass(slots=True)
class NodeStmtWhile:
    expr: NodeExpr
    scope: NodeScope


@dataclass(slots=True)
class NodeStmtDoWhile:
    scope: NodeScope
    expr: NodeExpr


@dataclass(slots=True)
class NodeStmtFor:
    ident_def: NodeStmtLet
    condition: NodeBinExprComp
    ident_assign: NodeStmtReassign
    scope: NodeScope


@dataclass(slots=True)
class NodeStmtBreak:
    pass


@dataclass(slots=True)
class NodeStmtPrint:
    content: NodeExpr | NodeTermChar


@dataclass(slots=True)
class NodeStmt:
    stmt_var: NodeStmtLet | NodeStmtExit | NodeScope | NodeStmtIf | NodeStmtReassign | NodeStmtWhile | NodeStmtBreak | NodeStmtFor | NodeStmtPrint


@dataclass(slots=True)
class NodeScope:
    stmts: list[NodeStmt]

@dataclass(slots=True)
class NodeProgram:
    stmts: list[NodeStmt]