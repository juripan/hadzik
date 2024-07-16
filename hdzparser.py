#TODO: fix the end lines acting weird while parsing, with if statements, scopes, etc.
from dataclasses import dataclass
from hdzlexer import Token
import hdztokentypes as tt
from hdzerrors import ErrorHandler


@dataclass(slots=True)
class NodeExpr:
    pass

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
    var: NodeTermIdent | NodeTermInt | NodeTermChar | NodeTermParen | NodeTermNot
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
    var: NodeBinExprAdd | NodeBinExprMulti | NodeBinExprSub | NodeBinExprDiv | NodeBinExprMod | NodeBinExprComp | NodeBinExprLogic


@dataclass(slots=True)
class NodeExpr:
    var: NodeTerm | NodeBinExpr


@dataclass(slots=True)
class NodeStmtExit:
    expr: NodeExpr


@dataclass(slots=True)
class NodeStmtLet:
    ident: Token
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
    expr: NodeExpr


@dataclass(slots=True)
class NodeStmt:
    stmt_var: NodeStmtLet | NodeStmtExit | NodeScope | NodeStmtIf | NodeStmtReassign | NodeStmtWhile | NodeStmtBreak | NodeStmtFor | NodeStmtPrint


@dataclass(slots=True)
class NodeScope:
    stmts: list[NodeStmt]

@dataclass(slots=True)
class NodeProgram:
    stmts: list[NodeStmt]



class Parser(ErrorHandler):
    def __init__(self, tokens, file_content):
        super().__init__(file_content)
        self.index: int = -1
        self.column_number = -1 # -1 means that theres no column number tracked
        self.all_tokens: list = tokens
        self.current_token: Token = None
        self.next_token()

    def next_token(self):
        if self.current_token is not None and self.current_token.type == tt.end_line:
            self.line_number += 1
        self.index += 1
        self.current_token = self.all_tokens[self.index] if self.index < len(self.all_tokens) else None

    def get_token_at(self, offset: int = 0) -> Token | None:
        return self.all_tokens[self.index + offset] if self.index + offset < len(self.all_tokens) else None

    def parse_term(self) -> NodeTerm | None:
        is_negative = False
        if self.current_token is not None and self.current_token.type == tt.minus:
            is_negative = True
            self.next_token()

        if self.current_token is not None and self.current_token.type == tt.integer:
            return NodeTerm(NodeTermInt(int_lit=self.current_token), is_negative)
        elif self.current_token is not None and self.current_token.type == tt.identifier:
            return NodeTerm(NodeTermIdent(ident=self.current_token), is_negative)
        elif self.current_token is not None and self.current_token.type == tt.char:
            return NodeTerm(NodeTermChar(char=self.current_token), is_negative)
        elif self.current_token is not None and self.current_token.type == tt.left_paren:
            self.next_token()
            expr = self.parse_expr()
            if expr is None:
                self.raise_error("Value", "Expected expression")

            if self.current_token is None or self.current_token.type != tt.right_paren:
                self.raise_error("Syntax", "expected ')'")

            return NodeTerm(NodeTermParen(expr), is_negative)
        elif self.current_token is not None and self.current_token.type == tt.not_:
            self.next_token()
            
            term = self.parse_term()
            if term is None:
                self.raise_error("Value", "Expected term")
            
            return NodeTerm(var=NodeTermNot(term=term))
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
            expr_lhs2 = NodeExpr(None) # prevents a recursion error, god knows why but it makes it work
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
            elif op.type == tt.percent:
                expr_lhs2.var = expr_lhs.var
                mod = NodeBinExprMod(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = mod
            elif op.type in (tt.is_equal, tt.is_not_equal, tt.larger_than, tt.less_than, tt.larger_than_or_eq, tt.less_than_or_eq):
                expr_lhs2.var = expr_lhs.var
                comp = NodeBinExprComp(lhs=expr_lhs2, rhs=expr_rhs, comp_sign=op)
                expr.var = comp
            elif op.type == tt.and_ or op.type == tt.or_:
                expr_lhs2.var = expr_lhs.var
                log = NodeBinExprLogic(lhs=expr_lhs2, rhs=expr_rhs, logical_operator=op)
                expr.var = log
            else:
                assert False # unreachable
            expr_lhs.var = expr
        return expr_lhs
    
    def parse_let(self) -> NodeStmtLet:
        self.next_token() # removes naj

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

        if self.current_token is not None and self.current_token.type not in (tt.end_line, tt.dash, tt.right_curly):
            self.raise_error("Syntax", "Expected endline") #TODO: make this more accurate

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
        
        if self.current_token is not None and self.current_token.type != tt.end_line:
            self.raise_error("Syntax", "Expected endline")

        return NodeStmtExit(expr=expr)

    def parse_scope(self) -> NodeScope:
        if self.current_token.type == tt.end_line:
            self.next_token()
        
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
        
        if self.current_token is not None and self.current_token.type == tt.end_line:
            self.next_token()

        return scope

    def parse_ifpred(self) -> NodeIfPred | None:
        if self.current_token is not None and self.current_token.type == tt.elif_:
            self.next_token()
            
            expr = self.parse_expr()
            if expr is None:
                self.raise_error("Value", "not able to evaluate expression")
            
            scope = self.parse_scope()

            ifpred = self.parse_ifpred()

            return NodeIfPred(NodeIfPredElif(expr, scope, ifpred))
        elif self.current_token is not None and self.current_token.type == tt.else_:
            self.next_token()
            
            scope = self.parse_scope()

            return NodeIfPred(NodeIfPredElse(scope))
        else:
            return None

    def parse_if(self) -> NodeStmtIf:
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "not able to parse expression")
        
        scope = self.parse_scope()

        ifpred = self.parse_ifpred()
        return NodeStmtIf(expr, scope, ifpred)

    def parse_while(self) -> NodeStmtWhile:
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "not able to parse expression")

        scope = self.parse_scope()
        return NodeStmtWhile(expr=expr, scope=scope)
    
    def parse_for_loop(self) -> NodeStmtFor:
        self.next_token()

        if self.current_token.type != tt.left_paren:
            self.raise_error("Syntax", "expected '('")
        self.next_token()

        ident_def = self.parse_let()

        if self.current_token.type != tt.dash:
            self.raise_error("Syntax", "expected ','")
        self.next_token()

        condition = self.parse_expr().var.var #gets the NodeTermComp
        if not isinstance(condition, NodeBinExprComp):
            self.raise_error("Syntax", "invalid condition")

        if self.current_token.type != tt.dash:
            self.raise_error("Syntax", "expected ','")
        self.next_token()

        assign = self.parse_reassign()
        
        if self.current_token.type != tt.right_paren:
            self.raise_error("Syntax", "expected ')'")
        self.next_token()

        scope = self.parse_scope()
        return NodeStmtFor(ident_def, condition, assign, scope)

    def parse_do_while(self) -> NodeStmtDoWhile:
        self.next_token()

        scope = self.parse_scope()
        
        if self.current_token is None or self.current_token.type != tt.while_:
            self.raise_error("Syntax", "expected 'kim'")
        self.next_token()

        if self.current_token is None or self.current_token.type != tt.left_paren:
            self.raise_error("Syntax", "expected '('")
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "invalid expression")

        if self.current_token is None or self.current_token.type != tt.right_paren:
            self.raise_error("Syntax", "expected ')'")
        self.next_token()

        return NodeStmtDoWhile(scope, expr)

    def parse_reassign(self) -> NodeStmtReassign:
        ident = self.current_token
        self.next_token()

        if self.current_token is not None and self.current_token.type == tt.increment:
            self.next_token()
            return NodeStmtReassign(var=NodeStmtReassignInc(ident))
        elif self.current_token is not None and self.current_token.type == tt.decrement:
            self.next_token()
            return NodeStmtReassign(var=NodeStmtReassignDec(ident))

        if self.current_token is None or self.current_token.type != tt.equals:
            self.raise_error("Syntax", "expected '='")
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "expected expression")
        
        if self.current_token is not None and self.current_token.type not in (tt.end_line, tt.right_curly, tt.right_paren):
            self.raise_error("Syntax", "Expected endline")
        
        return NodeStmtReassign(var=NodeStmtReassignEq(ident, expr))

    def parse_print(self) -> NodeStmtPrint:
        self.next_token() # removes print token
        
        if self.current_token.type != tt.left_paren:
            self.raise_error("Syntax", "Expected '('")
        self.next_token()

        expr = self.parse_expr()
        
        if expr is None:
            self.raise_error("Syntax", "Invalid print argument")

        if self.current_token and self.current_token.type != tt.right_paren:
            self.raise_error("Syntax", "Expected ')'")
        self.next_token()
        
        if self.current_token is not None and self.current_token.type != tt.end_line:
            self.raise_error("Syntax", "Expected endline")
        
        return NodeStmtPrint(expr)
    
    def parse_statement(self) -> NodeStmt | None:
        if self.current_token is None:
            return None
        elif self.current_token.type == tt.end_line:
            statement = "new_line"
            self.next_token()
        elif self.current_token.type == tt.exit_:
            statement = self.parse_exit()
        elif self.current_token.type == tt.print_:
            statement = self.parse_print()
        elif self.current_token.type == tt.let:
            statement = self.parse_let()
        elif self.current_token.type == tt.left_curly:
            statement = self.parse_scope()
        elif self.current_token.type == tt.if_:
            statement = self.parse_if()
        elif self.current_token.type == tt.identifier:
            statement = self.parse_reassign()
        elif self.current_token.type == tt.while_:
            statement = self.parse_while()
        elif self.current_token.type == tt.for_:
            statement = self.parse_for_loop()
        elif self.current_token.type == tt.do:
            statement = self.parse_do_while()
        elif self.current_token.type == tt.break_:
            self.next_token()
            statement = NodeStmtBreak()
        else:
            print(self.current_token)
            self.raise_error("Parsing", "cannot parse program correctly")
        return NodeStmt(stmt_var=statement)

    def parse_program(self) -> NodeProgram:
        program: NodeProgram = NodeProgram(stmts=[])
        while self.current_token is not None:
            program.stmts.append(self.parse_statement())
        return program
