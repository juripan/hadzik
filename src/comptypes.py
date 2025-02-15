from dataclasses import dataclass
from typing import Union, Optional
from hdztokentypes import TokenType

# primitive type, contains a size of object in bytes (8 bits)
size_bytes = int

size_words = str

@dataclass(slots=True)
class Token:
    type: TokenType
    line: int
    col: int
    value: Optional[str] = None

@dataclass(slots=True)
class NodeExpr: # type: ignore (has to be predeclared)
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
class NodeTermNot: # type: ignore (has to be predeclared)
    pass


@dataclass(slots=True)
class NodeTerm:
    var: Union[NodeTermIdent, NodeTermInt, NodeTermChar, NodeTermParen, NodeTermNot, NodeTermBool]
    negative: bool = False


@dataclass(slots=True)
class NodeTermNot:
    term: NodeTerm


@dataclass(slots=True)
class NodeBinExpr: # type: ignore (has to be predeclared)
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
    var: Union[NodeBinExprAdd, NodeBinExprMulti, NodeBinExprSub, NodeBinExprDiv, NodeBinExprMod, None]

@dataclass(slots=True)
class NodeLogicExpr:
    var: Union[NodeBinExprComp, NodeBinExprLogic, None]

@dataclass(slots=True)
class NodeExpr:
    var: Union[NodeTerm, NodeBinExpr, NodeLogicExpr, None]


@dataclass(slots=True)
class NodeStmtExit:
    expr: NodeExpr


@dataclass(slots=True)
class NodeStmtLet:
    ident: Token
    expr: NodeExpr
    type_: Token


class NodeScope: # type: ignore (has to be predeclared)
    pass

class NodeIfPred: # type: ignore (has to be predeclared)
    pass


@dataclass(slots=True)
class NodeIfPredElse:
    scope: NodeScope


@dataclass(slots=True)
class NodeIfPredElif:
    expr: NodeExpr
    scope: NodeScope
    pred: Optional[NodeIfPred]


@dataclass(slots=True)
class NodeIfPred:
    var: Union[NodeIfPredElif, NodeIfPredElse]


@dataclass(slots=True)
class NodeStmtIf:
    expr: NodeExpr
    scope: NodeScope
    ifpred: Optional[NodeIfPred]


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
    var: Union[NodeStmtReassignEq, NodeStmtReassignInc, NodeStmtReassignDec]


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
    content: Union[NodeExpr, NodeTermChar]


@dataclass(slots=True)
class NodeStmt: #TODO: make the str into a Newline type or EmptyStmt type
    stmt_var: Union[NodeStmtLet, NodeStmtExit, NodeScope, NodeStmtIf, NodeStmtReassign, NodeStmtWhile, NodeStmtDoWhile, NodeStmtBreak, NodeStmtFor, NodeStmtPrint, str]


@dataclass(slots=True)
class NodeScope:
    stmts: list[NodeStmt]

@dataclass(slots=True)
class NodeProgram:
    stmts: list[NodeStmt]
