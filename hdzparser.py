#TODO: fix the end lines acting weird while parsing, with if statements, scopes, etc.
from dataclasses import dataclass
from hdzlexer import Token
import hdztokentypes as tt
from hdzerrors import ErrorHandler


@dataclass(slots=True)
class NodeExpr:
    pass


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
class NodeTerm:
    var: NodeTermIdent | NodeTermInt | NodeTermParen


@dataclass(slots=True)
class NodeBinExpr:
    pass


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
class NodeBinExpr:
    var: NodeBinExprAdd | NodeBinExprMulti | NodeBinExprSub | NodeBinExprDiv


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
class NodeStmtAssign:
    ident: Token
    expr: NodeExpr


@dataclass(slots=True)
class NodeScope: #TODO: make a separate node for statements
    stmts: list[NodeStmtLet | NodeStmtExit | NodeScope | NodeStmtIf]

@dataclass(slots=True)
class NodeProgram:
    stmts: list[NodeStmtLet | NodeStmtExit | NodeScope | NodeStmtIf | NodeStmtAssign]


class Parser(ErrorHandler):
    def __init__(self, tokens, file_content):
        super().__init__(file_content)
        self.index: int = -1
        self.column_number = -1 # -1 means that theres no column number tracked
        self.all_tokens: list = tokens
        self.current_token: Token = None
        self.next_token()

    def next_token(self):
        self.index += 1
        self.current_token = self.all_tokens[self.index] if self.index < len(self.all_tokens) else None

    def get_token_at(self, offset: int = 0) -> Token | None:
        return self.all_tokens[self.index + offset] if self.index + offset < len(self.all_tokens) else None


    def parse_term(self) -> NodeTerm | None:
        if self.current_token is not None and self.current_token.type == tt.integer:
            return NodeTerm(var=NodeTermInt(int_lit=self.current_token))
        elif self.current_token is not None and self.current_token.type == tt.identifier:
            return NodeTerm(var=NodeTermIdent(ident=self.current_token))
        elif self.current_token is not None and self.current_token.type == tt.left_paren:
            self.next_token()
            expr = self.parse_expr()
            if expr is None:
                self.raise_error("Value", "Expected expression")

            if self.current_token is None or self.current_token.type != tt.right_paren:
                self.raise_error("Syntax", "expected ')'")

            return NodeTerm(var=NodeTermParen(expr=expr))
        else:
            return None

    def parse_expr(self, min_prec: int = 0) -> NodeExpr | None:
        term_lhs = self.parse_term()
        
        if term_lhs is None:
            return None
        self.next_token()

        expr_lhs = NodeExpr(var=term_lhs)

        while True:
            op: Token | None = self.current_token
            prec: int | None = tt.get_prec_level(op.type)

            if op is None or prec is None or prec < min_prec:
                break

            next_min_prec: int = prec + 1
            self.next_token()

            expr_rhs = self.parse_expr(next_min_prec)

            if expr_rhs is None:
                self.raise_error("Value", "unable to parse expression")

            expr = NodeBinExpr(None)
            expr_lhs2 = NodeExpr(None)
            if op.type == tt.plus:
                expr_lhs2.var = expr_lhs.var
                add = NodeBinExprAdd(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = add
            elif op.type == tt.star:
                expr_lhs2.var = expr_lhs.var
                multi = NodeBinExprMulti(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = multi
            elif op.type == tt.minus:
                expr_lhs2.var = expr_lhs.var
                sub = NodeBinExprSub(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = sub
            elif op.type == tt.slash:
                expr_lhs2.var = expr_lhs.var
                div = NodeBinExprDiv(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = div
            else:
                assert False # unreachable
            expr_lhs.var = expr
        return expr_lhs
    
    def parse_let(self) -> NodeStmtLet:
        self.next_token()

        if self.current_token.type != tt.identifier:
            self.raise_error("Syntax", "Expected identifier")
        ident = self.current_token
        self.next_token()

        if self.current_token.type != tt.equals:
            self.raise_error("Syntax", "Expected '='")
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Syntax", "Invalid expression")

        if self.current_token is None or self.current_token.type != tt.end_line:
            self.raise_error("Syntax", "Expected endline")

        return NodeStmtLet(ident, expr)

    def parse_exit(self) -> NodeStmtExit:
        self.next_token() # removes exit token
        
        if self.current_token.type != tt.left_paren:
            self.raise_error("Syntax", "Expected '('")
        self.next_token()

        expr = self.parse_expr()
        
        if expr is None:
            self.raise_error("Syntax", "Invalid expression")

        if self.current_token and self.current_token.type != tt.right_paren:
            self.raise_error("Syntax", "Expected ')'")
        self.next_token()
        
        if self.current_token is None or self.current_token.type != tt.end_line:
            self.raise_error("Syntax", "Expected endline")

        return NodeStmtExit(expr=expr)

    def parse_scope(self) -> NodeScope:
        if self.current_token is None or self.current_token.type != tt.left_curly:
            self.raise_error("Syntax", "expected '{'")
        self.next_token()  # left curly

        scope = NodeScope(stmts=[])
        while stmt := self.parse_statement():
            scope.stmts.append(stmt)
            if self.current_token and self.current_token.type == tt.right_curly:
                self.next_token() # right curly
                break
        else:
            self.raise_error("Syntax", "expected '}'")
        
        if self.current_token.type == tt.end_line:
            self.next_token()

        return scope

    def parse_ifpred(self) -> NodeIfPred | None:
        if self.current_token.type == tt.elif_:
            self.next_token()
            
            expr = self.parse_expr()
            if expr is None:
                self.raise_error("Value", "not able to evaluate expression")
            
            scope = self.parse_scope()

            ifpred = self.parse_ifpred()

            return NodeIfPred(NodeIfPredElif(expr, scope, ifpred))
        elif self.current_token.type == tt.else_:
            self.next_token()
            
            scope = self.parse_scope()

            return NodeIfPred(NodeIfPredElse(scope))
        else:
            return None

    def parse_if(self) -> NodeStmtIf:
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "not able to evaluate expression")
        
        scope = self.parse_scope()

        ifpred = self.parse_ifpred()
        return NodeStmtIf(expr, scope, ifpred)

    def parse_statement(self) -> NodeStmtExit | NodeStmtLet | NodeScope | NodeStmtAssign | str | None:
        if self.current_token is None:
            return None
        if self.current_token.type == tt.end_line:
            self.line_number += 1
            statement = "new_line"
            self.next_token()
        elif self.current_token.type == tt.exit_:
            statement = self.parse_exit()
        elif self.current_token.type == tt.let:
            statement = self.parse_let()
        elif self.current_token.type == tt.left_curly:
            statement = self.parse_scope()
        elif self.current_token.type == tt.if_:
            statement = self.parse_if()
        elif self.current_token.type == tt.identifier and self.get_token_at(1) is not None and self.get_token_at(1).type == tt.equals:
            ident = self.current_token
            self.next_token()
            self.next_token()

            expr = self.parse_expr()
            if expr is None:
                self.raise_error("Value", "expected expression")
            
            return NodeStmtAssign(ident, expr)
        else:
            self.raise_error("Parsing", "cannot parse program correctly")
        return statement

    def parse_program(self) -> NodeProgram:
        program: NodeProgram = NodeProgram(stmts=[])
        while self.current_token is not None:
            program.stmts.append(self.parse_statement())
        return program
