#TODO: fix the end lines acting weird while parsing, with if statements, scopes, etc.
#TODO: implement proper parsing for booleans and boolean expressions
from comptypes import * #uh-oh a wildcard import
from hdztokentypes import TokenType, get_prec_level
from hdzerrors import ErrorHandler


class Parser(ErrorHandler):
    def __init__(self, tokens: list[Token], file_content: str):
        super().__init__(file_content)
        self.index: int = -1
        self.column_number = -1 # -1 means that theres no column number tracked
        self.all_tokens: list[Token] = tokens
        self.current_token: Token | None = None
        self.next_token()

    def next_token(self):
        self.index += 1
        self.current_token = self.all_tokens[self.index] if self.index < len(self.all_tokens) else None

    def get_token_at(self, offset: int = 0) -> Token | None:
        return self.all_tokens[self.index + offset] if self.index + offset < len(self.all_tokens) else None
    
    def try_throw_error(self, token_type: TokenType, error_name: str, error_details: str) -> None:
        """
        checks if the current token is none or if its type is not the token type given,
        raises an error if the condition is true
        """
        if self.current_token is None or self.current_token.type != token_type:
            self.raise_error(error_name, error_details, self.current_token)


    def parse_char(self) -> NodeTermChar | None:
        if self.current_token is not None and self.current_token.type == TokenType.CHAR_LIT:
            char = self.current_token
            self.next_token()
            return NodeTermChar(char)
        else:
            return None

    def parse_term(self) -> NodeTerm | None:
        is_negative = False
        if self.current_token is not None and self.current_token.type == TokenType.MINUS:
            is_negative = True
            self.next_token()

        if self.current_token is not None and self.current_token.type == TokenType.INT_LIT:
            return NodeTerm(NodeTermInt(int_lit=self.current_token), is_negative)
        elif self.current_token is not None and self.current_token.type == TokenType.IDENT:
            return NodeTerm(NodeTermIdent(ident=self.current_token), is_negative)
        elif self.current_token is not None and self.current_token.type == TokenType.TRUE:
            self.current_token.value = "1"
            return NodeTerm(NodeTermBool(bool=self.current_token), is_negative)
        elif self.current_token is not None and self.current_token.type == TokenType.FALSE:
            self.current_token.value = "0"
            return NodeTerm(NodeTermBool(bool=self.current_token), is_negative)
        elif self.current_token is not None and self.current_token.type == TokenType.LEFT_PAREN:
            self.next_token()
            expr = self.parse_expr()
            if expr is None:
                self.raise_error("Value", "expected expression", self.current_token)

            self.try_throw_error(TokenType.RIGHT_PAREN, "Syntax", "expected ')'")

            assert expr is not None, "Should be handled in the if statement above"
            return NodeTerm(NodeTermParen(expr), is_negative)
        elif self.current_token is not None and self.current_token.type == TokenType.NOT:
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
                self.raise_error("Value", "unable to parse expression", self.current_token)
            assert expr_rhs is not None, "expression shouldn't be None, is handled in the above if statement"

            expr = NodeBinExpr(None) if op.type in (
                TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT
                ) else NodeLogicExpr(None)
            
            expr_lhs2 = NodeExpr(None) # prevents a recursion error, god knows why but it makes it work
            
            if op.type == TokenType.PLUS:
                expr_lhs2.var = expr_lhs.var
                add = NodeBinExprAdd(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = add # type: ignore (typechecking is being weird)
            elif op.type == TokenType.STAR:
                expr_lhs2.var = expr_lhs.var
                multi = NodeBinExprMulti(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = multi # type: ignore (typechecking is being weird)
            elif op.type == TokenType.MINUS:
                expr_lhs2.var = expr_lhs.var
                sub = NodeBinExprSub(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = sub # type: ignore (typechecking is being weird)
            elif op.type == TokenType.SLASH:
                expr_lhs2.var = expr_lhs.var
                div = NodeBinExprDiv(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = div # type: ignore (typechecking is being weird)
            elif op.type == TokenType.PERCENT:
                expr_lhs2.var = expr_lhs.var
                mod = NodeBinExprMod(lhs=expr_lhs2, rhs=expr_rhs)
                expr.var = mod # type: ignore (typechecking is being weird)
            elif op.type in (
                    TokenType.IS_EQUAL, TokenType.IS_NOT_EQUAL, 
                    TokenType.LARGER_THAN, TokenType.LESS_THAN, 
                    TokenType.LARGER_THAN_OR_EQ, TokenType.LESS_THAN_OR_EQ
                    ):
                expr_lhs2.var = expr_lhs.var
                comp = NodeBinExprComp(lhs=expr_lhs2, rhs=expr_rhs, comp_sign=op)
                expr.var = comp # type: ignore (typechecking is being weird)
            elif op.type == TokenType.AND or op.type == TokenType.OR:
                expr_lhs2.var = expr_lhs.var
                log = NodeBinExprLogic(lhs=expr_lhs2, rhs=expr_rhs, logical_operator=op)
                expr.var = log # type: ignore (typechecking is being weird)
            else:
                raise ValueError("unreachable! in parse_expr()")
            expr_lhs.var = expr
        return expr_lhs
    
    def parse_let(self) -> NodeStmtLet:
        type_def = self.current_token
        self.next_token() # removes type def

        self.try_throw_error(TokenType.IDENT, "Syntax", "expected valid identifier")
        ident = self.current_token
        self.next_token()

        self.try_throw_error(TokenType.EQUALS, "Syntax", "expected '='")
        self.next_token()

        assert type_def is not None, "type_def should never be None"
        if type_def.type in (TokenType.LET, TokenType.BOOL_DEF):
            value = self.parse_expr()
        else:
            value = None
            self.raise_error("Type", "type not defined", self.current_token)

        if value is None:
            self.raise_error("Syntax", "invalid expression", self.current_token)

        if self.current_token is not None and self.current_token.type not in (TokenType.ENDLINE, TokenType.COMMA, TokenType.RIGHT_CURLY):
            self.raise_error("Syntax", "expected endline", self.current_token) #TODO: make this more accurate

        assert ident is not None, "Identifier should never be None"
        assert value is not None, "Value should never be None, maybe a missing if value is None"
        return NodeStmtLet(ident, value, type_def)

    def parse_exit(self) -> NodeStmtExit:
        self.next_token() # removes exit token
        
        self.try_throw_error(TokenType.LEFT_PAREN, "Syntax", "expected '('")
        self.next_token()

        expr = self.parse_expr()
        
        if expr is None:
            self.raise_error("Syntax", "invalid expression", self.current_token)
        
        assert expr is not None, "expr shouldn't be None, handled in the above if statement"

        self.try_throw_error(TokenType.RIGHT_PAREN, "Syntax", "expected ')'")
        self.next_token()
        
        if self.current_token is not None and self.current_token.type not in (TokenType.ENDLINE, TokenType.RIGHT_CURLY, TokenType.RIGHT_PAREN):
            self.raise_error("Syntax", "expected endline", self.current_token)

        return NodeStmtExit(expr=expr)

    def parse_scope(self) -> NodeScope:
        if self.current_token is not None and self.current_token.type == TokenType.ENDLINE:
            self.next_token()
        
        self.try_throw_error(TokenType.LEFT_CURLY, "Syntax", "expected '{'")
        self.next_token()  # left curly

        scope = NodeScope(stmts=[])
        while stmt := self.parse_statement():
            scope.stmts.append(stmt)
            if self.current_token and self.current_token.type == TokenType.RIGHT_CURLY:
                self.next_token() # right curly
                break
        else:
            self.raise_error("Syntax", "expected '}'", self.current_token)
        
        if self.current_token and self.current_token.type == TokenType.ENDLINE:
            self.next_token()

        return scope

    def parse_ifpred(self) -> NodeIfPred | None:
        if self.current_token is not None and self.current_token.type == TokenType.ELIF:
            self.next_token()
            
            expr = self.parse_expr()
            if expr is None:
                self.raise_error("Value", "not able to evaluate expression", self.current_token)
            
            assert expr is not None, "expr shouldn't be None, handled in the previous if statement"
            
            scope = self.parse_scope()

            while self.current_token is not None and self.current_token.type == tt.end_line: # type: ignore (typechecker doesn't see I modify the value with method calls)
                self.next_token()

            ifpred = self.parse_ifpred()

            return NodeIfPred(NodeIfPredElif(expr, scope, ifpred))
        elif self.current_token is not None and self.current_token.type == TokenType.ELSE:
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

        while self.current_token is not None and self.current_token.type == TokenType.ENDLINE:
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
        return NodeStmtWhile(expr=expr, scope=scope)
    
    def parse_for_loop(self) -> NodeStmtFor:
        self.next_token()

        self.try_throw_error(TokenType.LEFT_PAREN, "Syntax", "expected '('")
        self.next_token()

        ident_def = self.parse_let()

        self.try_throw_error(TokenType.COMMA, "Syntax", "expected ','")
        self.next_token()

        expr = self.parse_expr()
        if expr is None or expr.var is None:
            self.raise_error("Syntax", "missing condition", self.current_token)
        
        assert expr is not None, "expr shouldn't be None, handled in the previous if statement"
        assert expr.var is not None, "expr.var shouldn't be None, handled in the previous if statement"

        condition = expr.var.var # gets the NodeTermComp

        if not isinstance(condition, NodeBinExprComp):
            self.raise_error("Syntax", "invalid condition", self.current_token)

        self.try_throw_error(TokenType.COMMA, "Syntax", "expected ','")
        self.next_token()

        assign = self.parse_reassign()
        
        self.try_throw_error(TokenType.RIGHT_PAREN, "Syntax", "expected ')'")
        self.next_token()

        scope = self.parse_scope()
        return NodeStmtFor(ident_def, condition, assign, scope)  # type: ignore (type checker is going insane here)

    def parse_do_while(self) -> NodeStmtDoWhile:
        self.next_token()

        scope = self.parse_scope()
        
        self.try_throw_error(TokenType.WHILE, "Syntax", "expected 'kim'")
        self.next_token()

        self.try_throw_error(TokenType.LEFT_PAREN, "Syntax", "expected '('")
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "invalid expression", self.current_token)
        
        assert expr is not None, "expr shouldn't be None here, handled by the previous if condition"

        self.try_throw_error(TokenType.RIGHT_PAREN, "Syntax", "expected ')'")
        self.next_token()

        return NodeStmtDoWhile(scope, expr)

    def parse_reassign(self) -> NodeStmtReassign:
        self.try_throw_error(TokenType.IDENT, "Syntax", "expected identifier")
        ident = self.current_token
        self.next_token()
        
        assert ident is not None, "identifier shouldn't be None here, triggered the parse_reassign function"
        
        if self.current_token is not None and self.current_token.type == TokenType.INCREMENT:
            self.next_token()
            return NodeStmtReassign(var=NodeStmtReassignInc(ident))
        elif self.current_token is not None and self.current_token.type == TokenType.DECREMENT:
            self.next_token()
            return NodeStmtReassign(var=NodeStmtReassignDec(ident))

        self.try_throw_error(TokenType.EQUALS, "Syntax", "expected '='")
        self.next_token()

        expr = self.parse_expr()
        if expr is None:
            self.raise_error("Value", "expected expression", self.current_token)
        
        assert expr is not None, "expr shouldn't be None here, handled by the previous if condition"
        
        if self.current_token is not None and self.current_token.type not in (TokenType.ENDLINE, TokenType.RIGHT_CURLY, TokenType.RIGHT_PAREN):
            self.raise_error("Syntax", "expected endline", self.current_token)
        
        return NodeStmtReassign(var=NodeStmtReassignEq(ident, expr))

    def parse_print(self) -> NodeStmtPrint:
        self.next_token() # removes print token

        self.try_throw_error(TokenType.LEFT_PAREN, "Syntax", "expected '('")
        self.next_token()

        if self.current_token is not None and self.current_token.type == TokenType.CHAR_LIT:
            cont = self.parse_char()
        else:
            cont = self.parse_expr()

        if cont is None:
            self.raise_error("Syntax", "Invalid print argument", self.current_token)
        
        assert cont is not None, "content shouldn't be None, handled by the previous if statement"

        self.try_throw_error(TokenType.RIGHT_PAREN, "Syntax", "expected ')'")
        self.next_token()
        
        if self.current_token is not None and self.current_token.type not in (TokenType.ENDLINE, TokenType.RIGHT_CURLY):
            self.raise_error("Syntax", "expected endline", self.current_token)
        
        return NodeStmtPrint(cont)
    
    def parse_statement(self) -> NodeStmt | None:
        statement = None
        if self.current_token is None:
            return None
        elif self.current_token.type == TokenType.ENDLINE:
            statement = "new_line"
            self.next_token()
        elif self.current_token.type == TokenType.EXIT:
            statement = self.parse_exit()
        elif self.current_token.type == TokenType.PRINT:
            statement = self.parse_print()
        elif self.current_token.type in (TokenType.LET, TokenType.BOOL_DEF):
            statement = self.parse_let()
        elif self.current_token.type == TokenType.LEFT_CURLY:
            statement = self.parse_scope()
        elif self.current_token.type == TokenType.IF:
            statement = self.parse_if()
        elif self.current_token.type == TokenType.IDENT:
            statement = self.parse_reassign()
        elif self.current_token.type == TokenType.WHILE:
            statement = self.parse_while()
        elif self.current_token.type == TokenType.FOR:
            statement = self.parse_for_loop()
        elif self.current_token.type == TokenType.DO:
            statement = self.parse_do_while()
        elif self.current_token.type == TokenType.BREAK:
            self.next_token()
            statement = NodeStmtBreak()
        else:
            self.raise_error("Syntax", "invalid statement form", self.current_token)
        
        assert statement is not None, "statement should never be None, handled by the if statements above"
        return NodeStmt(stmt_var=statement)

    def parse_program(self) -> NodeProgram:
        program: NodeProgram = NodeProgram(stmts=[])
        while self.current_token is not None:
            stmt = self.parse_statement()
            assert stmt is not None, "statement should not be None, only if there is a None token"
            program.stmts.append(stmt)
        return program
