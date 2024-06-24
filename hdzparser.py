from dataclasses import dataclass
from hdzlexer import Token
import hdztokentypes as tt
from hdzerrors import ErrorHandler


@dataclass(slots=True)
class NodeExprIdent:
    ident: Token #tt.identifier | tt.integer


@dataclass(slots=True)
class NodeExprInt:
    int_lit: Token #tt.integer


@dataclass(slots=True)
class NodeBinExpr:
    pass


@dataclass(slots=True)
class NodeExpr:
    pass


@dataclass(slots=True)
class BinExprAdd:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class BinExprSub:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class BinExprMulti:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class BinExprDiv:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class NodeBinExpr:
    var: BinExprAdd | BinExprSub | BinExprMulti | BinExprDiv


@dataclass(slots=True)
class NodeExpr:
    var: NodeExprInt | NodeExprIdent


@dataclass(slots=True)
class NodeStmtExit:
    expr: NodeExpr


@dataclass(slots=True)
class NodeStmtLet:
    ident: Token  # tt.ident
    expr: NodeExpr


@dataclass(slots=True)
class NodeProgram:
    stmts: list[NodeStmtLet | NodeStmtExit]


class Parser(ErrorHandler):
    def __init__(self, tokens, file_content):
        super().__init__(file_content)
        self.index: int = 0
        self.all_tokens: list = tokens
        self.current_token: Token = self.all_tokens[self.index]

    def next_token(self):
        self.index += 1
        self.current_token = self.all_tokens[self.index] if self.index < len(self.all_tokens) else None

    def look_ahead(self, offset: int = 0) -> Token | None:
        return self.all_tokens[self.index + offset]

    def parse_expr(self, token: Token) -> NodeExpr | None:
        if token.type in (tt.floating_number, tt.integer):
            if self.look_ahead(1).type not in tt.bin_op:
                self.next_token()
                return NodeExpr(var=NodeExprInt(int_lit=token))
            # TODO: handle binary expressions here
        elif token.type == tt.identifier:
            self.next_token()
            return NodeExpr(NodeExprIdent(ident=token))
        else:
            return None

    def parse_let(self) -> NodeStmtLet:
        self.next_token()
        let_stmt: NodeStmtLet
        if self.current_token.type != tt.identifier:
            self.raise_error("Syntax", "Expected identifier")
        let_stmt = NodeStmtLet(ident=self.current_token, expr=None)
        self.next_token()

        if self.current_token.type != tt.equals:
            self.raise_error("Syntax", "Expected '='")
        self.next_token()

        expr = self.parse_expr(self.current_token)
        if expr is None:
            self.raise_error("Syntax", "Invalid expression")
        let_stmt.expr = expr
        return let_stmt

    def parse_exit(self) -> NodeStmtExit:
        self.next_token() # removes exit token
        exit_stmt: NodeStmtExit
        if self.current_token.type != tt.left_paren:
            self.raise_error("Syntax", "Expected '('")
        self.next_token()

        expr = self.parse_expr(self.current_token)
        
        if expr is None:
            self.raise_error("Syntax", "Invalid expression")
        
        exit_stmt = NodeStmtExit(expr=expr)

        if self.current_token and self.current_token.type != tt.right_paren:
            self.raise_error("Syntax", "Expected ')'")
        self.next_token()
        return exit_stmt

    def parse_program(self) -> NodeProgram:
        program: NodeProgram = NodeProgram(stmts=[])
        while self.current_token is not None:
            if self.current_token.type == tt.end_line:
                self.line_number += 1
                self.next_token()
            elif self.current_token.type == tt.exit_:
                program.stmts.append(self.parse_exit())
            elif self.current_token.type == tt.let:
                program.stmts.append(self.parse_let())
            else:
                self.raise_error("Parsing", "cannot parse program correctly")
        return program
