from dataclasses import dataclass
from hdzlexer import Token
import hdztokentypes as tt
from hdzerrors import ErrorHandler


@dataclass(slots=True)
class NodeTermIdent:
    ident: Token


@dataclass(slots=True)
class NodeTermInt:
    int_lit: Token


@dataclass(slots=True)
class NodeTerm:
    var: NodeTermIdent | NodeTermInt


@dataclass(slots=True)
class NodeBinExpr:
    pass


@dataclass(slots=True)
class NodeExpr:
    pass


@dataclass(slots=True)
class NodeBinExprAdd:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class NodeBinExprMulti:
    lhs: NodeExpr
    rhs: NodeExpr


@dataclass(slots=True)
class NodeBinExpr:
    var: NodeBinExprAdd | NodeBinExprMulti


@dataclass(slots=True)
class NodeExpr:
    var: NodeTerm | NodeBinExpr


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

    def get_token_at(self, offset: int = 0) -> Token | None:
        return self.all_tokens[self.index + offset] if self.index + offset < len(self.all_tokens) else None

    def parse_term(self) -> NodeTerm | None:
        if self.current_token.type in (tt.floating_number, tt.integer):
            int_lit = self.current_token
            return NodeTerm(var=NodeTermInt(int_lit))
        elif self.current_token.type == tt.identifier:
            ident = self.current_token
            return NodeTerm(var=NodeTermIdent(ident))
        else:
            return None

    def parse_expr(self) -> NodeExpr | None:
        term = self.parse_term()

        if term:
            if self.get_token_at(1).type in tt.bin_op:
                parsed_lhs = NodeExpr(term)
                self.next_token()

                if self.current_token is None or self.current_token.type not in (tt.plus, tt.plus):
                    self.raise_error("Value", f"Unsupported type operator: {self.current_token.type}")
                self.next_token()
                
                parsed_rhs = self.parse_expr()
                if parsed_rhs is None:
                    self.raise_error("Value", "expected expression")
                return NodeExpr(var=NodeBinExpr(var=NodeBinExprAdd(parsed_lhs, parsed_rhs)))
            else:
                return NodeExpr(var=term)
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

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Syntax", "Invalid expression")
        let_stmt.expr = expr
        self.next_token()

        if self.current_token is None or self.current_token.type != tt.end_line:
            self.raise_error("Syntax", "Expected endline")

        return let_stmt

    def parse_exit(self) -> NodeStmtExit:
        self.next_token() # removes exit token
        exit_stmt: NodeStmtExit
        if self.current_token.type != tt.left_paren:
            self.raise_error("Syntax", "Expected '('")
        self.next_token()

        expr = self.parse_expr()
        
        if expr is None:
            self.raise_error("Syntax", "Invalid expression")
        self.next_token()

        exit_stmt = NodeStmtExit(expr=expr)

        if self.current_token and self.current_token.type != tt.right_paren:
            self.raise_error("Syntax", "Expected ')'")
        self.next_token()
        
        if self.current_token is None or self.current_token.type != tt.end_line:
            self.raise_error("Syntax", "Expected endline")

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
