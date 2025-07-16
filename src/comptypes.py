from dataclasses import dataclass
from typing import Union, Optional
from tokentypes import *


#################
## Lexer types ###################################################
#################


@dataclass(slots=True)
class Token:
    type: token_type
    line: int
    col: int
    value: Optional[str] = None


##################
## Parser types ###################################################
##################


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
class NodeTermStr:
    string: Token
    length: str

@dataclass(slots=True)
class NodeTermIdent:
    ident: Token
    negative: bool = False


@dataclass(slots=True)
class NodeTermInt:
    int_lit: Token
    negative: bool = False


@dataclass(slots=True)
class NodeTermParen:
    expr: NodeExpr
    negative: bool = False


@dataclass(slots=True)
class NodeTermNot: # type: ignore (has to be predeclared)
    pass

@dataclass(slots=True)
class NodeTermBNot: # type: ignore (has to be predeclared)
    pass

@dataclass(slots=True)
class NodeTermCast:
    expr: NodeExpr
    type: Token

@dataclass(slots=True)
class NodeTermArray:
    exprs: list[NodeExpr]


@dataclass(slots=True)
class NodeTerm:
    var: Union[
        NodeTermIdent, NodeTermInt, NodeTermChar, NodeTermStr, 
        NodeTermParen, NodeTermNot, NodeTermBool, NodeTermCast,
        NodeTermBNot, NodeTermArray
    ]
    index: Optional[NodeExpr] = None


@dataclass(slots=True)
class NodeTermNot:
    term: NodeTerm

@dataclass(slots=True)
class NodeTermBNot:
    term: NodeTerm

@dataclass(slots=True)
class NodeBinExpr:
    lhs: NodeExpr
    rhs: NodeExpr
    op: Token

@dataclass(slots=True)
class NodeExpr:
    var: Union[NodeTerm, NodeBinExpr, None]


@dataclass(slots=True)
class NodeStmtExit:
    expr: NodeExpr

@dataclass(slots=True)
class NodeType:
    type: token_type
    subtype: token_type | None = None

@dataclass(slots=True)
class NodeStmtDeclare:
    ident: Token
    expr: NodeExpr
    type_: NodeType
    is_const: bool = False


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
    ident: NodeTerm
    rvalue: NodeExpr


@dataclass(slots=True)
class NodeStmtReassignInc:
    ident: NodeTerm


@dataclass(slots=True)
class NodeStmtReassignDec:
    ident: NodeTerm


@dataclass(slots=True)
class NodeStmtReassign:
    var: Union[
        NodeStmtReassignEq, NodeStmtReassignInc, NodeStmtReassignDec
    ]


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
    ident_def: NodeStmtDeclare
    condition: NodeExpr
    ident_assign: NodeStmtReassign
    scope: NodeScope


@dataclass(slots=True)
class NodeStmtBreak:
    break_tkn: Token


@dataclass(slots=True)
class NodeStmtPrint:
    content: NodeExpr
    cont_type: token_type


@dataclass(slots=True)
class NodeStmtEmpty: # empty line that only contains newline token
    pass


@dataclass(slots=True)
class NodeStmt:
    stmt_var: Union[
        NodeStmtDeclare, NodeStmtExit, NodeScope, 
        NodeStmtIf, NodeStmtReassign, NodeStmtWhile, 
        NodeStmtDoWhile, NodeStmtBreak, NodeStmtFor, NodeStmtPrint, NodeStmtEmpty
    ]


@dataclass(slots=True)
class NodeScope:
    stmts: list[NodeStmt]


@dataclass(slots=True)
class NodeProgram:
    stmts: list[NodeStmt]

#######################
## Typechecker types ###################################################
#######################

@dataclass(slots=True)
class StackItem:
    """
    class that stores the type name of the value,
    if its a constant variable (if it is one)
    and its location in the source code via Token (for error reporting)
    """
    type: token_type
    loc: tuple[int, int] | Token
    sub_type: token_type | None = None
    name: str = ""
    is_const: bool = False

#####################
## Generator types ###################################################
#####################

"""
primitive type, contains a size of object in bytes (8 bits)
"""
size_bytes = int
"""
primitive type, contains a size of object in words (WORD, QWORD, etc.)
"""
size_words = str

@dataclass(slots=True)
class VariableContext:
    name: str
    loc: int
    type: NodeType
    size_w: size_words
    size_b: size_bytes
    
    def __repr__(self) -> str:
        return f"VC('{self.name}' loc={self.loc} type={self.type.type, self.type.subtype} size={self.size_b})"
