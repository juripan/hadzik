from hdzerrors import ErrorHandler
from comptypes import *

# TODO: make a type checker that runs after parsing, before code generation

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
            # self.typecheck_scope(stmt.stmt_var)
            ...
        elif isinstance(stmt.stmt_var, NodeStmtIf):
            # self.typecheck_if(stmt.stmt_var)
            ...
        elif isinstance(stmt.stmt_var, NodeStmtReassign):
            self.typecheck_reassign(stmt.stmt_var)
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
            vars = tuple(filter(lambda x: x[0] == term.var.ident.value, self.variables)) # type: ignore
            self.push_stack(vars[-1][1])
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
