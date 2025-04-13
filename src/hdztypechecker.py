from hdzerrors import ErrorHandler
from comptypes import *

class TypeChecker(ErrorHandler):
    stack: list[token_type] = []
    variables: list[tuple[str, token_type]] = [] # stores all variables and their types

    def __init__(self, program: NodeProgram, file_content: str) -> None:
        super().__init__(file_content)
        self.main_program = program

    def push_stack(self, tt: token_type):
        self.stack.append(tt)

    def pop_stack(self):
        return self.stack.pop()


    def typecheck_program(self):
        for stmt in self.main_program.stmts:
            assert stmt is not None, "None statement shouldn't make it here"
            self.typecheck_statement(stmt)
            self.line_number+=1

    def typecheck_statement(self, stmt: NodeStmt):
        if isinstance(stmt.stmt_var, NodeStmtExit):
            self.typecheck_exit(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtDeclare):
            self.typecheck_decl(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeScope):
            self.typecheck_scope(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtIf):
            self.typecheck_if_statement(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtReassign):
            self.typecheck_reassign(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtWhile):
            self.typecheck_while(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtDoWhile):
            self.typecheck_dowhile(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtFor):
            self.typecheck_for(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtPrint):
            # self.typecheck_print(stmt.stmt_var)
            ...
    
    def typecheck_term(self, term: NodeTerm):
        if isinstance(term.var, NodeTermInt):
            assert term.var.int_lit.value is not None, "term.var.int_lit.value shouldn't be None, probably a parsing error"

            self.push_stack(INT_DEF)
        elif isinstance(term.var, NodeTermIdent):
            vars = tuple(filter(lambda x: x[0] == term.var.ident.value, self.variables)) # type: ignore
            self.push_stack(vars[-1][1])
        elif isinstance(term.var, NodeTermBool):
            assert term.var.bool.value is not None, "shouldn't be None here"
            self.push_stack(BOOL_DEF)
        elif isinstance(term.var, NodeTermParen):
            self.typecheck_expression(term.var.expr)
        elif isinstance(term.var, NodeTermNot):
            self.typecheck_term(term.var.term) # type: ignore (typechecker freaking out)

    def typecheck_binary_expression(self, bin_expr: NodeBinExpr):
        self.typecheck_expression(bin_expr.var.lhs) # type: ignore
        self.typecheck_expression(bin_expr.var.rhs) # type: ignore
        a = self.pop_stack()
        if a != INT_DEF:
            self.raise_error("Type", f"expected type `{INT_DEF}`, got `{a}`", )
        b = self.pop_stack()
        if b != INT_DEF:
            self.raise_error("Type", f"expected type `{INT_DEF}`, got `{b}`")
        self.push_stack(INT_DEF)

    def typecheck_logical_expression(self, log_expr: NodeExprLogic):
        self.typecheck_expression(log_expr.lhs)
        self.typecheck_expression(log_expr.rhs)
        a = self.pop_stack()
        if a != BOOL_DEF:
            self.raise_error("Type", f"expected type `{BOOL_DEF}`, got `{a}`", )
        b = self.pop_stack()
        if b != BOOL_DEF:
            self.raise_error("Type", f"expected type `{BOOL_DEF}`, got `{b}`")
        self.push_stack(BOOL_DEF)

    def typecheck_predicate_expression(self, pred_expr: NodePredExpr):
        self.typecheck_expression(pred_expr.lhs)
        self.typecheck_expression(pred_expr.rhs)
        
        a = self.pop_stack()
        if a != INT_DEF:
            self.raise_error("Type", f"expected type `{INT_DEF}`, got `{a}`", )
        b = self.pop_stack()
        if b != INT_DEF:
            self.raise_error("Type", f"expected type `{INT_DEF}`, got `{b}`")
        self.push_stack(BOOL_DEF)

    def typecheck_bool_expression(self, bool_expr: NodeExprBool):
        if isinstance(bool_expr.var, NodePredExpr):
            self.typecheck_predicate_expression(bool_expr.var)
        elif isinstance(bool_expr.var, NodeExprLogic):
            self.typecheck_logical_expression(bool_expr.var)

    def typecheck_expression(self, expr: NodeExpr):
        if isinstance(expr.var, NodeTerm):
            self.typecheck_term(expr.var)
        elif isinstance(expr.var, NodeBinExpr):
            self.typecheck_binary_expression(expr.var)
        elif isinstance(expr.var, NodeExprBool):
            self.typecheck_bool_expression(expr.var)

    def typecheck_exit(self, exit_stmt: NodeStmtExit):
        self.typecheck_expression(exit_stmt.expr)

        if (type_ := self.stack.pop()) != INT_DEF:
            self.raise_error("Type", f"expected type `{INT_DEF}`, got `{type_}`")
    
    def typecheck_decl(self, decl_stmt: NodeStmtDeclare):
        self.typecheck_expression(decl_stmt.expr)
        if self.stack[-1] != decl_stmt.type_.type:
            self.raise_error("Type", f"expected type `{decl_stmt.type_.type}`, got `{self.stack[-1]}`")
        self.variables.append((decl_stmt.ident.value, decl_stmt.type_.type)) # type: ignore (freaking out about str | None)
    
    def typecheck_reassign(self, reassign_stmt: NodeStmtReassign):
        found_vars = tuple(filter(lambda x: x[0] == reassign_stmt.var.ident.value, self.variables)) # type: ignore

        if not found_vars:
            self.raise_error("Value", f"undeclared identifier: {reassign_stmt.var.ident.value}", reassign_stmt.var.ident)
        
        if isinstance(reassign_stmt.var, NodeStmtReassignEq):
            self.typecheck_expression(reassign_stmt.var.expr)
            if (type_ := self.pop_stack()) != found_vars[-1][1]:
                self.raise_error("Type", f"expected type `{found_vars[-1][1]}`, got `{type_}`")
        elif isinstance(reassign_stmt.var, (NodeStmtReassignInc, NodeStmtReassignDec)): # type: ignore (using an else branch to catch errors)
            if found_vars[-1][1] != INT_DEF:
                self.raise_error("Type", f"cannot increment or decrement a variable of `{found_vars[-1][1]}` type")
        else:
            raise ValueError("out or reach")
    
    def typecheck_scope(self, scope_stmt: NodeScope):
        for stmt in scope_stmt.stmts:
            self.typecheck_statement(stmt)
    
    def typecheck_if_statement(self, if_stmt: NodeStmtIf):
        self.typecheck_expression(if_stmt.expr)
        if (type_ := self.pop_stack()) not in (BOOL_DEF, INT_DEF):
            self.raise_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{type_}`")
        
        self.typecheck_scope(if_stmt.scope)
        
        if if_stmt.ifpred is not None:
            self.typecheck_if_predicate(if_stmt.ifpred)
    
    def typecheck_if_predicate(self, ifpred: NodeIfPred):
        if isinstance(ifpred.var, NodeIfPredElif):
            self.typecheck_expression(ifpred.var.expr)
            if (type_ := self.pop_stack()) not in (BOOL_DEF, INT_DEF):
                self.raise_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{type_}`")
            self.typecheck_scope(ifpred.var.scope)
            if ifpred.var.pred is not None:
                self.typecheck_if_predicate(ifpred.var.pred)
        elif isinstance(ifpred.var, NodeIfPredElse): # type: ignore (uses else for error catching)
            self.typecheck_scope(ifpred.var.scope)
        else:
            raise ValueError("Unreachable")
    
    def typecheck_while(self, while_stmt: NodeStmtWhile):
        self.typecheck_expression(while_stmt.expr)
        if (type_ := self.pop_stack()) not in (BOOL_DEF, INT_DEF):
            self.raise_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{type_}`")
        self.typecheck_scope(while_stmt.scope)
    
    def typecheck_dowhile(self, do_while_stmt: NodeStmtDoWhile):
        self.typecheck_scope(do_while_stmt.scope)
        self.typecheck_expression(do_while_stmt.expr)
        if (type_ := self.pop_stack()) not in (BOOL_DEF, INT_DEF):
            self.raise_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{type_}`")
    
    def typecheck_for(self, for_stmt: NodeStmtFor):
        self.typecheck_decl(for_stmt.ident_def)

        self.typecheck_predicate_expression(for_stmt.condition)
        if (type_ := self.pop_stack()) != BOOL_DEF:
            self.raise_error("Type", f"expected type `{BOOL_DEF}`, got `{type_}`")
        
        self.typecheck_scope(for_stmt.scope)

        self.typecheck_reassign(for_stmt.ident_assign)