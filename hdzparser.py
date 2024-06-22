from dataclasses import dataclass
from hdzlexer import Token
import token_types as tt
from hdzerrors import raise_error


@dataclass
class NodeIdent:
    token: Token #tt.identifier | tt.integer


@dataclass
class NodeFactor:
    number: Token #tt.integer | tt.floating_number


@dataclass
class NodeBinExpr:
    pass


@dataclass
class NodeExpr:
    pass


@dataclass
class BinExprAdd:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass
class BinExprSub:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass
class BinExprMulti:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass
class BinExprDiv:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass
class NodeBinExpr:
    var: BinExprAdd | BinExprSub | BinExprMulti | BinExprDiv


@dataclass
class NodeExpr:
    var: NodeBinExpr | NodeFactor | NodeIdent


@dataclass
class NodeExit:
    node_expr: NodeExpr


@dataclass
class NodeStmt:
    var: NodeExit


@dataclass
class NodeProgram:
    stmts: list[NodeStmt]


class Parser:
    def __init__(self, tokens, file):
        self.index: int = 0
        self.row_index: int = 1
        self.file: str = file
        self.all_tokens: list = tokens
        self.current_token: Token = self.all_tokens[self.index]

    def next_token(self):
        self.index += 1
        self.current_token = self.all_tokens[self.index] if self.index < len(self.all_tokens) else None

    def look_ahead(self, offset: int = 0) -> Token | None:
        return self.all_tokens[self.index + offset]

    def parse_expr(self, token) -> NodeExpr | None:
        if token.type in (tt.floating_number, tt.integer):
            if self.look_ahead(1).type not in tt.bin_op:
                self.next_token()
                return NodeExpr(var=NodeFactor(token))
            # TODO: handle binary expressions here
        else:
            return None

    def parse_exit(self) -> NodeExit:
        self.next_token()
        exit_node: NodeExit
        while self.current_token is not None:
            if self.current_token.type == tt.left_paren:
                self.next_token()

                expr = self.parse_expr(self.current_token)
                if expr is None:
                    raise_error("Syntax", "Invalid expression", self.file, self.row_index)
                elif expr.var.number.type == tt.floating_number:
                    raise_error("Value", "exit cant use float", self.file, self.row_index)
                exit_node = NodeExit(node_expr=expr)

                if self.current_token and self.current_token.type != tt.right_paren:
                    raise_error("Syntax", "Expected ')'", self.file, self.row_index)
                self.next_token()
                    
                if self.current_token and self.current_token.type == tt.end_line:
                    self.next_token()
                return exit_node
            else:
                raise_error("Syntax", "Expected '('", self.file, self.row_index)
        raise_error("Syntax", "Missing Enter", self.file, self.row_index)

    def parse_program(self) -> NodeProgram:
        program: NodeProgram = NodeProgram(stmts=[])
        while self.current_token is not None:
            if self.current_token.type == tt.exit_:
                program.stmts.append(self.parse_exit())
            elif self.current_token.type == tt.end_line:
                self.next_token()
                self.row_index += 1
            else:
                raise_error("Parsing", "cannot parse program correctly", self.file, self.row_index)
        return program
