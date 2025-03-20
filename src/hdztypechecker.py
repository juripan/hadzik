
# TODO: make a type checker that runs after parsing, before code generation

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

    def typecheck_statement(self, stmt: NodeStmt):
        if isinstance(stmt.stmt_var, NodeStmtExit):
            self.typecheck_exit(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtLet):
            # self.typecheck_let(stmt.stmt_var)
            ...
        elif isinstance(stmt.stmt_var, NodeScope):
            # self.typecheck_scope(stmt.stmt_var)
            ...
        elif isinstance(stmt.stmt_var, NodeStmtIf):
            # self.typecheck_if(stmt.stmt_var)
            ...
        elif isinstance(stmt.stmt_var, NodeStmtReassign):
            # self.typecheck_reassign(stmt.stmt_var)
            ...
        elif isinstance(stmt.stmt_var, NodeStmtWhile):
            # self.typecheck_while(stmt.stmt_var)
            ...
        elif isinstance(stmt.stmt_var, NodeStmtDoWhile):
            # self.typecheck_dowhile(stmt.stmt_var)
            ...
        elif isinstance(stmt.stmt_var, NodeStmtFor):
            # self.typecheck_for(stmt.stmt_var)
            ...
        elif isinstance(stmt.stmt_var, NodeStmtPrint):
            # self.typecheck_print(stmt.stmt_var)
            ...
    
    def typecheck_term(self, term: NodeTerm):
        if isinstance(term.var, NodeTermInt):
            assert term.var.int_lit.value is not None, "term.var.int_lit.value shouldn't be None, probably a parsing error"

            self.push_stack(INT_DEF)
        elif isinstance(term.var, NodeTermIdent):
            raise NotImplementedError("tracking identifiers and their types is not implemented")
        elif isinstance(term.var, NodeTermBool):
            assert term.var.bool.value is not None, "shouldn't be None here"
            self.push_stack(BOOL_DEF)
        elif isinstance(term.var, NodeTermParen):
            self.typecheck_expression(term.var.expr)
        elif isinstance(term.var, NodeTermNot):
            self.typecheck_term(term.var.term) # type: ignore (typechecker freaking out)

    def typecheck_expression(self, expr: NodeExpr):
        if isinstance(expr.var, NodeTerm):
            self.typecheck_term(expr.var)
        elif isinstance(expr.var, NodeBinExpr):
            raise NotImplementedError("binary expression checking not implemented yet")
        elif isinstance(expr.var, NodeExprBool):
            raise NotImplementedError("bool expression checking not implemented yet")

    def typecheck_exit(self, exit_stmt: NodeStmtExit):
        self.typecheck_expression(exit_stmt.expr)

        if self.stack.pop() != INT_DEF:
            self.raise_error("Type", "expected type `int`")
