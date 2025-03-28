from comptypes import * # uh-oh a wildcard import
import hdztokentypes as tt
from hdzerrors import ErrorHandler

#TODO: implement proper parsing for booleans and boolean expressions


class Parser(ErrorHandler):
    index: int = -1
    column_number = -1 # -1 means that theres no column number tracked
    current_token: Token | None = None

    def __init__(self, tokens: list[Token], file_content: str):
        super().__init__(file_content)
        self.all_tokens: list[Token] = tokens
        self.map_parse_func: dict[token_type, function]  = {
            tt.EXIT: self.parse_exit,
            tt.PRINT: self.parse_print,
            tt.INT_DEF: self.parse_let,
            tt.BOOL_DEF: self.parse_let,
            tt.LEFT_CURLY: self.parse_scope,
            tt.IF: self.parse_if,
            tt.IDENT: self.parse_reassign,
            tt.WHILE: self.parse_while,
            tt.FOR: self.parse_for_loop,
            tt.DO: self.parse_do_while,
            tt.BREAK: self.parse_break,
            tt.ENDLINE: self.parse_endline,
        }
        self.next_token() # here to set the first token

    def next_token(self) -> Token | None:
        self.index += 1
        self.current_token = self.all_tokens[self.index] if self.index < len(self.all_tokens) else None

    def get_token_at(self, offset: int = 0) -> Token | None:
        return self.all_tokens[self.index + offset] if self.index + offset < len(self.all_tokens) else None
    
    def try_throw_error(self, token_type: token_type, error_name: str, error_details: str) -> None:
        """
        checks if the current token is none or if its type is not the token type given,
        raises an error if the condition is true
        """
        if self.current_token is None or self.current_token.type != token_type:
            self.raise_error(error_name, error_details, self.current_token)


    def parse_char(self) -> NodeTermChar | None:
        if self.current_token is not None and self.current_token.type == tt.CHAR_LIT:
            char = self.current_token
            self.next_token()
            return NodeTermChar(char)
        else:
            return None

    def parse_term(self) -> NodeTerm | None:
        is_negative = False
        if self.current_token is not None and self.current_token.type == tt.MINUS:
            is_negative = True
            self.next_token()

        if self.current_token is not None and self.current_token.type == tt.INT_LIT:
            return NodeTerm(NodeTermInt(int_lit=self.current_token), is_negative)
        elif self.current_token is not None and self.current_token.type == tt.IDENT:
            return NodeTerm(NodeTermIdent(ident=self.current_token), is_negative)
        elif self.current_token is not None and self.current_token.type == tt.TRUE:
            self.current_token.value = "1"
            return NodeTerm(NodeTermBool(bool=self.current_token))
        elif self.current_token is not None and self.current_token.type == tt.FALSE:
            self.current_token.value = "0"
            return NodeTerm(NodeTermBool(bool=self.current_token))
        elif self.current_token is not None and self.current_token.type == tt.LEFT_PAREN:
            self.next_token()
            expr = self.parse_expr()
            if expr is None:
                self.raise_error("Value", "expected expression", self.current_token)

            self.try_throw_error(tt.RIGHT_PAREN, "Syntax", "expected ')'")

            assert expr is not None, "Should be handled in the if statement above"
            return NodeTerm(NodeTermParen(expr=expr), is_negative)
        elif self.current_token is not None and self.current_token.type == tt.NOT:
            self.next_token()
            
            term = self.parse_term()
            if term is None:
                self.raise_error("Value", "expected term", self.current_token)
            
            assert term is not None, "Should be handled in the if statement above"
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
            prec: int | None = None

            if op:
                prec: int | None = get_prec_level(op.type)

            if op is None or prec is None or prec < min_prec:
                break

            next_min_prec: int = prec + 1
            self.next_token()

            expr_rhs = self.parse_expr(next_min_prec)

            if expr_rhs is None:
                self.raise_error("Value", "invalid expression", self.current_token)
            assert expr_rhs is not None, "expression shouldn't be None, is handled in the above if statement"

            expr = NodeBinExpr(None) if op.type in (
                tt.PLUS, tt.MINUS, tt.STAR, tt.SLASH, tt.PERCENT
                ) else NodeExprBool(None)
            
            expr_lhs2 = NodeExpr(None) # prevents a recursion error, god knows why but it makes it work
            
            if op.type == tt.PLUS:
                expr_lhs2.var = expr_lhs.var
                add = NodeBinExprAdd(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = add # type: ignore (typechecking is being weird)
            elif op.type == tt.STAR:
                expr_lhs2.var = expr_lhs.var
                multi = NodeBinExprMulti(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = multi # type: ignore (typechecking is being weird)
            elif op.type == tt.MINUS:
                expr_lhs2.var = expr_lhs.var
                sub = NodeBinExprSub(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = sub # type: ignore (typechecking is being weird)
            elif op.type == tt.SLASH:
                expr_lhs2.var = expr_lhs.var
                div = NodeBinExprDiv(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = div # type: ignore (typechecking is being weird)
            elif op.type == tt.PERCENT:
                expr_lhs2.var = expr_lhs.var
                mod = NodeBinExprMod(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = mod # type: ignore (typechecking is being weird)
            elif op.type in COMPARISONS:
                expr_lhs2.var = expr_lhs.var
                comp = NodePredExpr(lhs=expr_lhs2, rhs=expr_rhs, comp_sign=op)
                expr.var = comp # type: ignore (typechecking is being weird)
            elif op.type == tt.AND or op.type == tt.OR:
                expr_lhs2.var = expr_lhs.var
                log = NodeExprLogic(lhs=expr_lhs2, rhs=expr_rhs, logical_operator=op)
                expr.var = log # type: ignore (typechecking is being weird)
            else:
                raise ValueError("unreachable! in parse_expr()")
            expr_lhs.var = expr
        return expr_lhs
    
    def parse_let(self) -> NodeStmtLet:
        type_def = self.current_token
        self.next_token() # removes type def

        self.try_throw_error(tt.IDENT, "Syntax", "expected valid identifier")
        ident = self.current_token
        self.next_token()

        self.try_throw_error(tt.EQUALS, "Syntax", "expected '='")
        self.next_token()

        assert type_def is not None, "type_def should never be None"
        if type_def.type in (tt.INT_DEF, tt.BOOL_DEF):
            value = self.parse_expr()
        else:
            value = None
            self.raise_error("Type", "type not defined", self.current_token)

        if value is None:
            self.raise_error("Syntax", "invalid expression", self.current_token)

        assert ident is not None, "Identifier should never be None"
        assert value is not None, "Value should never be None, maybe a missing if value is None"
        return NodeStmtLet(ident, value, type_def)

    def parse_exit(self) -> NodeStmtExit:
        self.next_token() # removes exit token
        
        self.try_throw_error(tt.LEFT_PAREN, "Syntax", "expected '('")
        self.next_token()

        expr = self.parse_expr()
        
        if expr is None:
            self.raise_error("Syntax", "invalid expression", self.current_token)
        
        assert expr is not None, "expr shouldn't be None, handled in the above if statement"

        self.try_throw_error(tt.RIGHT_PAREN, "Syntax", "expected ')'")
        self.next_token()

        return NodeStmtExit(expr=expr)

    def parse_scope(self) -> NodeScope:
        if self.current_token is not None and self.current_token.type == tt.ENDLINE:
            self.next_token()
        
        start_curly = self.current_token
        self.try_throw_error(tt.LEFT_CURLY, "Syntax", "expected '{'")
        self.next_token()  # left curly

        scope = NodeScope(stmts=[])
        while stmt := self.parse_statement():
            scope.stmts.append(stmt)
            if not isinstance(stmt.stmt_var, (NodeStmtEmpty, NodeStmtIf)) \
                    and self.current_token and self.current_token.type != tt.RIGHT_CURLY:
                self.try_throw_error(tt.ENDLINE, "Syntax", "expected new line")
                self.next_token()
            if self.current_token and self.current_token.type == tt.RIGHT_CURLY:
                self.next_token() # right curly
                return scope
        else:
            self.raise_error("Syntax", "unclosed scope starting here", start_curly)
        
        if self.current_token and self.current_token.type == tt.RIGHT_CURLY:
            print("AAAAAAAA")
            self.next_token() # right curly (for empty statement with no statements inside)
        return scope

    def parse_ifpred(self) -> NodeIfPred | None:
        if self.current_token is not None and self.current_token.type == tt.ELIF:
            self.next_token()
            
            expr = self.parse_expr()
            if expr is None:
                self.raise_error("Value", "not able to evaluate expression", self.current_token)
            
            assert expr is not None, "expr shouldn't be None, handled in the previous if statement"
            
            scope = self.parse_scope()

            ifpred = self.parse_ifpred()

            return NodeIfPred(NodeIfPredElif(expr, scope, ifpred))
        elif self.current_token is not None and self.current_token.type == tt.ELSE:
            self.next_token()
            
            scope = self.parse_scope()

            return NodeIfPred(NodeIfPredElse(scope))
        else:
            return None

    def parse_if(self) -> NodeStmtIf:
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "not able to parse expression", self.current_token)

        assert expr is not None, "expr shouldn't be None, handled in the previous if statement"
        
        scope = self.parse_scope()

        while self.current_token is not None and self.current_token.type == tt.ENDLINE:
            self.next_token()

        ifpred = self.parse_ifpred()
        return NodeStmtIf(expr, scope, ifpred)

    def parse_while(self) -> NodeStmtWhile:
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "not able to parse expression", self.current_token)
        
        assert expr is not None, "expr shouldn't be None, handled in the previous if statement"

        scope = self.parse_scope()
        return NodeStmtWhile(expr, scope)
    
    def parse_for_loop(self) -> NodeStmtFor:
        self.next_token()

        self.try_throw_error(tt.LEFT_PAREN, "Syntax", "expected '('")
        self.next_token()

        ident_def = self.parse_let()

        self.try_throw_error(tt.COMMA, "Syntax", "expected ','")
        self.next_token()

        expr = self.parse_expr()
        if expr is None or expr.var is None:
            self.raise_error("Syntax", "missing condition", self.current_token)
        
        assert expr is not None, "expr shouldn't be None, handled in the previous if statement"
        assert expr.var is not None, "expr.var shouldn't be None, handled in the previous if statement"

        condition = expr.var.var # gets the NodePredExpr

        if not isinstance(condition, NodePredExpr):
            self.raise_error("Syntax", "invalid condition", self.current_token)

        self.try_throw_error(tt.COMMA, "Syntax", "expected ','")
        self.next_token()

        assign = self.parse_reassign()
        
        self.try_throw_error(tt.RIGHT_PAREN, "Syntax", "expected ')'")
        self.next_token()

        scope = self.parse_scope()
        return NodeStmtFor(ident_def, condition, assign, scope)  # type: ignore (type checker is going insane here)

    def parse_do_while(self) -> NodeStmtDoWhile:
        self.next_token()

        scope = self.parse_scope()
        
        self.try_throw_error(tt.WHILE, "Syntax", "expected 'kim'")
        self.next_token()

        self.try_throw_error(tt.LEFT_PAREN, "Syntax", "expected '('")
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "invalid expression", self.current_token)
        
        assert expr is not None, "expr shouldn't be None here, handled by the previous if condition"

        self.try_throw_error(tt.RIGHT_PAREN, "Syntax", "expected ')'")
        self.next_token()

        return NodeStmtDoWhile(scope, expr)

    def parse_reassign(self) -> NodeStmtReassign:
        self.try_throw_error(tt.IDENT, "Syntax", "expected identifier")
        ident = self.current_token
        self.next_token()
        
        assert ident is not None, "identifier shouldn't be None here, triggered the parse_reassign function"
        
        if self.current_token is not None and self.current_token.type == tt.INCREMENT:
            self.next_token()
            return NodeStmtReassign(var=NodeStmtReassignInc(ident))
        elif self.current_token is not None and self.current_token.type == tt.DECREMENT:
            self.next_token()
            return NodeStmtReassign(var=NodeStmtReassignDec(ident))

        self.try_throw_error(tt.EQUALS, "Syntax", "expected '='")
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "expected expression", self.current_token)
        
        assert expr is not None, "expr shouldn't be None here, handled by the previous if condition"
        
        return NodeStmtReassign(var=NodeStmtReassignEq(ident, expr))

    def parse_print(self) -> NodeStmtPrint:
        self.next_token() # removes print token

        self.try_throw_error(tt.LEFT_PAREN, "Syntax", "expected '('")
        self.next_token()

        if self.current_token is not None and self.current_token.type == tt.CHAR_LIT:
            cont = self.parse_char()
        else:
            cont = self.parse_expr()

        if cont is None:
            self.raise_error("Syntax", "Invalid print argument", self.current_token)
        
        assert cont is not None, "content shouldn't be None, handled by the previous if statement"

        self.try_throw_error(tt.RIGHT_PAREN, "Syntax", "expected ')'")
        self.next_token()
        
        return NodeStmtPrint(cont)
    
    def parse_break(self):
        self.next_token()
        return NodeStmtBreak()

    def parse_endline(self):
        self.next_token()
        return NodeStmtEmpty()
    
    def parse_statement(self) -> NodeStmt | None:
        if self.current_token is None:
            return None
        statement = None
        
        parse_func: function | None = self.map_parse_func.get(self.current_token.type)
        
        if self.current_token.type == tt.RIGHT_CURLY: # here to handle fully empty scopes like this -> {{}}
            return NodeStmt(stmt_var=NodeStmtEmpty())
        if parse_func is None:
            self.raise_error("Syntax", "invalid statement start", self.current_token)
        assert parse_func is not None, "shouldn't be None here"

        statement = parse_func() # type: ignore (I know the type but the checker keeps panicking)
        
        assert statement is not None, "statement should never be None, handled by the if statements above"
        return NodeStmt(stmt_var=statement) # type: ignore (I know the type but the checker keeps panicking)

    def parse_program(self) -> NodeProgram:
        program: NodeProgram = NodeProgram(stmts=[])
        while self.current_token is not None:
            stmt = self.parse_statement()
            if not isinstance(stmt.stmt_var, (NodeStmtEmpty, NodeScope, NodeStmtIf)) and self.current_token:  # type: ignore (shouldn't be a problem if its None)
                self.try_throw_error(tt.ENDLINE, "Syntax", "expected new line")
                self.next_token()
            program.stmts.append(stmt)
        return program
