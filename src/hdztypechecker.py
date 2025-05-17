from dataclasses import dataclass
from hdzerrors import ErrorHandler
from comptypes import *

@dataclass(slots=True)
class StackItem:
    """
    class that stores the type name of the variable (if it is one),
    if its a constant variable (if it is one)
    and its location in the source code via Token (for error reporting)
    """
    type_: token_type
    token: Token
    name: str = ""
    is_const: bool = False


class TypeChecker(ErrorHandler):
    stack: list[StackItem] = []
    variables: list[StackItem] = [] # stores all variables and their types

    def __init__(self, program: NodeProgram, file_content: str) -> None:
        super().__init__(file_content)
        self.main_program = program

    def push_stack(self, item: StackItem):
        """
        pushes the given item onto the stack,
        is a separate function for tracking and debugging purposes
        """
        self.stack.append(item)

    def pop_stack(self):
        """
        pops the top item off the stack,
        is a separate function for tracking and debugging purposes
        """
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
            self.typecheck_print(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtEmpty):
            pass
        elif isinstance(stmt.stmt_var, NodeStmtBreak): # type: ignore
            pass
        else:
            raise ValueError(f"Unreachable {stmt.stmt_var}")
    
    def typecheck_term(self, term: NodeTerm):
        if isinstance(term.var, NodeTermInt):
            assert term.var.int_lit.value is not None, "term.var.int_lit.value shouldn't be None, probably a parsing error"
            self.push_stack(StackItem(INT_DEF, term.var.int_lit))
        elif isinstance(term.var, NodeTermIdent):
            vars: tuple[StackItem, ...] = tuple(filter(lambda x: x.name == term.var.ident.value, self.variables)) # type: ignore
            if not vars:
                self.raise_error("Value", f"variable was not declared: {term.var.ident.value}", term.var.ident)
            self.push_stack(StackItem(vars[-1].type_, term.var.ident, vars[-1].name))
        elif isinstance(term.var, NodeTermBool):
            assert term.var.bool.value is not None, "shouldn't be None here"
            self.push_stack(StackItem(BOOL_DEF, term.var.bool))
        elif isinstance(term.var, NodeTermParen):
            self.typecheck_expression(term.var.expr)
        elif isinstance(term.var, NodeTermChar):
            self.push_stack(StackItem(CHAR_DEF, term.var.char))
        elif isinstance(term.var, NodeTermNot): # type: ignore
            self.typecheck_term(term.var.term) # type: ignore
            if self.stack[-1].type_ != BOOL_DEF:
                self.raise_error("Type", f"expected type `{BOOL_DEF}`, got `{self.stack[-1].type_}`", self.stack[-1].token)
        else:
            raise ValueError("Unreachable")

    def typecheck_binary_expression(self, bin_expr: NodeBinExpr):
        self.typecheck_expression(bin_expr.var.lhs) # type: ignore
        self.typecheck_expression(bin_expr.var.rhs) # type: ignore
        a = self.pop_stack()
        if a.type_ != INT_DEF:
            self.raise_error("Type", f"expected type `{INT_DEF}`, got `{a.type_}`", a.token)
        b = self.pop_stack()
        if b.type_ != INT_DEF:
            self.raise_error("Type", f"expected type `{INT_DEF}`, got `{b.type_}`", b.token)
        self.push_stack(a)

    def typecheck_logical_expression(self, log_expr: NodeExprLogic):
        self.typecheck_expression(log_expr.lhs)
        self.typecheck_expression(log_expr.rhs)
        a = self.pop_stack()
        if a.type_ != BOOL_DEF:
            self.raise_error("Type", f"expected type `{BOOL_DEF}`, got `{a.type_}`", a.token)
        b = self.pop_stack()
        if b.type_ != BOOL_DEF:
            self.raise_error("Type", f"expected type `{BOOL_DEF}`, got `{b.type_}`", b.token)
        self.push_stack(a)

    def typecheck_predicate_expression(self, pred_expr: NodePredExpr):
        self.typecheck_expression(pred_expr.lhs)
        self.typecheck_expression(pred_expr.rhs)
        
        a = self.pop_stack()
        if a.type_ != INT_DEF:
            self.raise_error("Type", f"expected type `{INT_DEF}`, got `{a.type_}`", a.token)
        b = self.pop_stack()
        if b.type_ != INT_DEF:
            self.raise_error("Type", f"expected type `{INT_DEF}`, got `{b.type_}`", b.token)
        self.push_stack(StackItem(BOOL_DEF, a.token))

    def typecheck_bool_expression(self, bool_expr: NodeExprBool):
        if isinstance(bool_expr.var, NodePredExpr):
            self.typecheck_predicate_expression(bool_expr.var)
        elif isinstance(bool_expr.var, NodeExprLogic):
            self.typecheck_logical_expression(bool_expr.var)
        else:
            raise ValueError("Unreachable")

    def typecheck_expression(self, expr: NodeExpr):
        if isinstance(expr.var, NodeTerm):
            self.typecheck_term(expr.var)
        elif isinstance(expr.var, NodeBinExpr):
            self.typecheck_binary_expression(expr.var)
        elif isinstance(expr.var, NodeExprBool):
            self.typecheck_bool_expression(expr.var)
        else:
            raise ValueError("Unreachable")

    def typecheck_exit(self, exit_stmt: NodeStmtExit):
        self.typecheck_expression(exit_stmt.expr)

        if (item := self.stack.pop()).type_ != INT_DEF:
            self.raise_error("Type", f"expected type `{INT_DEF}`, got `{item.type_}`", item.token)
    
    def typecheck_decl(self, decl_stmt: NodeStmtDeclare):
        """
        checks if the type fits the keyword used to declare the variable,
        if the type is supposed to be inferred then it just takes whatever type is on top of the stack
        """
        self.typecheck_expression(decl_stmt.expr)

        if decl_stmt.type_.type == INFER_DEF:
            decl_stmt.type_.type = self.stack[-1].type_
        elif self.stack[-1].type_ != decl_stmt.type_.type:
            self.raise_error("Type", f"expected type `{decl_stmt.type_.type}`, got `{self.stack[-1].type_}`", decl_stmt.type_)
        self.variables.append(StackItem(decl_stmt.type_.type, decl_stmt.ident, decl_stmt.ident.value, decl_stmt.is_const)) # type: ignore (freaking out about str | None)
    
    def typecheck_reassign(self, reassign_stmt: NodeStmtReassign):
        found_vars = tuple(filter(lambda x: x.name == reassign_stmt.var.ident.value, self.variables))

        if not found_vars:
            self.raise_error("Value", f"undeclared identifier: {reassign_stmt.var.ident.value}", reassign_stmt.var.ident)
        elif found_vars[-1].is_const:
            self.raise_error("Value", f"reassignment of const identifier: {reassign_stmt.var.ident.value}", reassign_stmt.var.ident)
        
        if isinstance(reassign_stmt.var, NodeStmtReassignEq):
            self.typecheck_expression(reassign_stmt.var.expr)
            if (item := self.pop_stack()).type_ != found_vars[-1].type_:
                self.raise_error("Type", f"expected type `{found_vars[-1].type_}`, got `{item.type_}`", reassign_stmt.var.ident)
        elif isinstance(reassign_stmt.var, (NodeStmtReassignInc, NodeStmtReassignDec)): # type: ignore (using an else branch to catch errors)
            if found_vars[-1].type_ != INT_DEF:
                self.raise_error("Type", f"cannot increment or decrement a variable of `{found_vars[-1].type_}` type", found_vars[-1].token)
        else:
            raise ValueError("out or reach")
    
    def typecheck_scope(self, scope_stmt: NodeScope):
        for stmt in scope_stmt.stmts:
            self.typecheck_statement(stmt)
    
    def typecheck_if_statement(self, if_stmt: NodeStmtIf):
        self.typecheck_expression(if_stmt.expr)
        if (item := self.pop_stack()).type_ not in (BOOL_DEF, INT_DEF):
            self.raise_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{item.type_}`", item.token)
        
        self.typecheck_scope(if_stmt.scope)
        
        if if_stmt.ifpred is not None:
            self.typecheck_if_predicate(if_stmt.ifpred)
    
    def typecheck_if_predicate(self, ifpred: NodeIfPred):
        if isinstance(ifpred.var, NodeIfPredElif):
            self.typecheck_expression(ifpred.var.expr)
            if (item := self.pop_stack()).type_ not in (BOOL_DEF, INT_DEF):
                self.raise_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{item.type_}`", item.token)
            self.typecheck_scope(ifpred.var.scope)
            if ifpred.var.pred is not None:
                self.typecheck_if_predicate(ifpred.var.pred)
        elif isinstance(ifpred.var, NodeIfPredElse): # type: ignore (uses else for error catching)
            self.typecheck_scope(ifpred.var.scope)
        else:
            raise ValueError("Unreachable")
    
    def typecheck_while(self, while_stmt: NodeStmtWhile):
        self.typecheck_expression(while_stmt.expr)
        if (item := self.pop_stack()).type_ not in (BOOL_DEF, INT_DEF):
            self.raise_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{item.type_}`", item.token)
        self.typecheck_scope(while_stmt.scope)
    
    def typecheck_dowhile(self, do_while_stmt: NodeStmtDoWhile):
        self.typecheck_scope(do_while_stmt.scope)
        self.typecheck_expression(do_while_stmt.expr)
        if (item := self.pop_stack()).type_ not in (BOOL_DEF, INT_DEF):
            self.raise_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{item.type_}`", item.token)
    
    def typecheck_for(self, for_stmt: NodeStmtFor):
        self.typecheck_decl(for_stmt.ident_def)

        self.typecheck_predicate_expression(for_stmt.condition)
        if (item := self.pop_stack()).type_ != BOOL_DEF:
            self.raise_error("Type", f"expected type `{BOOL_DEF}`, got `{item.type_}`", item.token)
        
        self.typecheck_scope(for_stmt.scope)

        self.typecheck_reassign(for_stmt.ident_assign)
    
    def typecheck_print(self, print_stmt: NodeStmtPrint):
        self.typecheck_expression(print_stmt.content)
        if (item := self.pop_stack()).type_ != CHAR_DEF:
            self.raise_error("Type", f"expected type `{CHAR_DEF}`, got `{item.type_}`", item.token)
