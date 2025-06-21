from dataclasses import dataclass
from errors import ErrorHandler
from comptypes import *

@dataclass(slots=True)
class StackItem:
    """
    class that stores the type name of the variable (if it is one),
    if its a constant variable (if it is one)
    and its location in the source code via Token (for error reporting)
    """
    type_: token_type
    loc: tuple[int, int]
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


    def check_program(self):
        for stmt in self.main_program.stmts:
            assert stmt is not None, "None statement shouldn't make it here"
            self.check_statement(stmt)
            self.line_number += 1

    def check_statement(self, stmt: NodeStmt):
        if isinstance(stmt.stmt_var, NodeStmtExit):
            self.check_exit(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtDeclare):
            self.check_decl(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeScope):
            self.check_scope(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtIf):
            self.check_if_statement(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtReassign):
            self.check_reassign(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtWhile):
            self.check_while(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtDoWhile):
            self.check_do_while(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtFor):
            self.check_for(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtPrint):
            self.check_print(stmt.stmt_var)
        elif isinstance(stmt.stmt_var, NodeStmtEmpty):
            pass
        elif isinstance(stmt.stmt_var, NodeStmtBreak): # type: ignore
            pass
        else:
            raise ValueError(f"Unreachable {stmt.stmt_var}")
    
    def check_term(self, term: NodeTerm):
        if term.index is not None:
            term2 = NodeTerm(term.var)
            self.check_term(term2)
            if (res := self.pop_stack()).type_ not in COLLECTIONS:
                self.compiler_error("Type", f"expected indexable type, got `{res.type_}`", res.loc)
            else:
                res.type_ = get_collection_subtype[res.type_]
            
            self.check_expression(term.index)
            if (idx := self.pop_stack()).type_ != INT_DEF:
                self.compiler_error("Type", f"expected type `{INT_DEF}`, got `{idx.type_}`", idx.loc)
            self.push_stack(res)
        elif isinstance(term.var, NodeTermInt):
            assert term.var.int_lit.value is not None, "term.var.int_lit.value shouldn't be None, probably a parsing error"
            self.push_stack(StackItem(INT_DEF, (term.var.int_lit.line, term.var.int_lit.col)))
        elif isinstance(term.var, NodeTermIdent):
            vars: tuple[StackItem, ...] = tuple(filter(lambda x: x.name == term.var.ident.value, self.variables)) # type: ignore
            
            if not vars:
                self.compiler_error("Value", f"variable was not declared: {term.var.ident.value}", term.var.ident)
            
            self.push_stack(StackItem(vars[-1].type_, (term.var.ident.line, term.var.ident.col), vars[-1].name))
        elif isinstance(term.var, NodeTermBool):
            assert term.var.bool.value is not None, "shouldn't be None here"
            self.push_stack(StackItem(BOOL_DEF, (term.var.bool.line, term.var.bool.col)))
        elif isinstance(term.var, NodeTermParen):
            self.check_expression(term.var.expr)
            if term.var.negative and self.stack[-1].type_ != INT_DEF:
                self.compiler_error("Type", f"`{self.stack[-1].type_}` cannot be negative", self.stack[-1].loc)
        elif isinstance(term.var, NodeTermChar):
            self.push_stack(StackItem(CHAR_DEF, (term.var.char.line, term.var.char.col)))
        elif isinstance(term.var, NodeTermStr):
            self.push_stack(StackItem(STR_DEF, (term.var.string.line, term.var.string.col)))
        elif isinstance(term.var, NodeTermNot):
            self.check_term(term.var.term) # type: ignore
            if self.stack[-1].type_ != BOOL_DEF:
                self.compiler_error("Type", f"expected type `{BOOL_DEF}`, got `{self.stack[-1].type_}`", self.stack[-1].loc)
        elif isinstance(term.var, NodeTermCast):
            if term.var.type.type == STR_DEF:
                #TODO: implement typecasting for strings
                raise NotImplementedError("typecasting to a string is not implemented yet")
            self.check_expression(term.var.expr)
            if self.stack[-1].type_ == STR_DEF and term.var.type.type == CHAR_DEF:
                self.compiler_error("Type", f"cannot cast `{STR_DEF}` to `{CHAR_DEF}`", term.var.type)
            self.stack[-1].type_ = term.var.type.type
        else:
            raise ValueError("Unreachable")

    def check_binary_expression(self, bin_expr: NodeBinExpr):
        self.check_expression(bin_expr.lhs)
        self.check_expression(bin_expr.rhs)
        a = self.pop_stack()
        b = self.pop_stack()
        if bin_expr.op.type in COMPARISONS:
            if a.type_ not in (INT_DEF, CHAR_DEF):
                self.compiler_error("Type", f"expected type `{INT_DEF}`, got `{a.type_}`", a.loc)
            if b.type_ not in (INT_DEF, CHAR_DEF):
                self.compiler_error("Type", f"expected type `{INT_DEF}`, got `{b.type_}`", b.loc)
            self.push_stack(StackItem(BOOL_DEF, a.loc))
        elif bin_expr.op.type in (OR, AND):
            if a.type_ != BOOL_DEF:
                self.compiler_error("Type", f"expected type `{BOOL_DEF}`, got `{a.type_}`", a.loc)
            if b.type_ != BOOL_DEF:
                self.compiler_error("Type", f"expected type `{BOOL_DEF}`, got `{b.type_}`", b.loc)
            self.push_stack(a)
        else:
            if a.type_ != INT_DEF:
                self.compiler_error("Type", f"expected type `{INT_DEF}`, got `{a.type_}`", a.loc)
            if b.type_ != INT_DEF:
                self.compiler_error("Type", f"expected type `{INT_DEF}`, got `{b.type_}`", b.loc)
            self.push_stack(a)

    def check_expression(self, expr: NodeExpr):
        if isinstance(expr.var, NodeTerm):
            self.check_term(expr.var)
        elif isinstance(expr.var, NodeBinExpr):
            self.check_binary_expression(expr.var)
        else:
            raise ValueError("Unreachable")

    def check_exit(self, exit_stmt: NodeStmtExit):
        self.check_expression(exit_stmt.expr)

        if (item := self.stack.pop()).type_ != INT_DEF:
            self.compiler_error("Type", f"expected type `{INT_DEF}`, got `{item.type_}`", item.loc)
    
    def check_decl(self, decl_stmt: NodeStmtDeclare):
        """
        checks if the type fits the keyword used to declare the variable,
        if the type is supposed to be inferred then it just takes whatever type is on top of the stack
        """
        self.check_expression(decl_stmt.expr)

        if decl_stmt.type_.type == INFER_DEF:
            decl_stmt.type_.type = self.stack[-1].type_
        elif self.stack[-1].type_ != decl_stmt.type_.type:
            self.compiler_error("Type", f"expected type `{decl_stmt.type_.type}`, got `{self.stack[-1].type_}`", decl_stmt.type_)
        self.variables.append(StackItem(decl_stmt.type_.type, decl_stmt.ident, decl_stmt.ident.value, decl_stmt.is_const)) # type: ignore (freaking out about str | None)
    
    def check_reassign(self, reassign_stmt: NodeStmtReassign):
        assert isinstance(reassign_stmt.var.ident.var, NodeTermIdent), "has to be this, error in parsing"
        found_vars = tuple(filter(lambda x: x.name == reassign_stmt.var.ident.var.ident.value, self.variables)) # type: ignore

        if not found_vars:
            self.compiler_error("Value", f"undeclared identifier: {reassign_stmt.var.ident.var.ident.value}", reassign_stmt.var.ident.var.ident)
        elif found_vars[-1].is_const:
            self.compiler_error("Value", f"modification of const identifier: {reassign_stmt.var.ident.var.ident.value}", reassign_stmt.var.ident.var.ident)

        if isinstance(reassign_stmt.var, NodeStmtReassignEq):
            self.check_expression(reassign_stmt.var.rvalue)
            item = self.pop_stack()
            # if item.type_ == STR_DEF:
            #     self.compiler_error("Type", f"reassigning of type `{item.type_}` is not allowed", reassign_stmt.var.ident.var.ident)
            if reassign_stmt.var.ident.index is not None:
                if found_vars[-1].type_ not in COLLECTIONS:
                    self.compiler_error("Type", f"expected indexable type, got `{found_vars[-1].type_}`", found_vars[-1].loc)
            elif item.type_ != found_vars[-1].type_:
                self.compiler_error("Type", f"expected type `{found_vars[-1].type_}`, got `{item.type_}`", reassign_stmt.var.ident.var.ident)
        elif isinstance(reassign_stmt.var, (NodeStmtReassignInc, NodeStmtReassignDec)):
            if found_vars[-1].type_ != INT_DEF:
                self.compiler_error("Type", f"cannot increment or decrement a variable of `{found_vars[-1].type_}` type", found_vars[-1].loc)
        else:
            raise ValueError("out of reach")
    
    def check_scope(self, scope_stmt: NodeScope):
        for stmt in scope_stmt.stmts:
            self.check_statement(stmt)
    
    def check_if_statement(self, if_stmt: NodeStmtIf):
        self.check_expression(if_stmt.expr)
        if (item := self.pop_stack()).type_ not in (BOOL_DEF, INT_DEF):
            self.compiler_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{item.type_}`", item.loc)
        
        self.check_scope(if_stmt.scope)
        
        if if_stmt.ifpred is not None:
            self.check_if_predicate(if_stmt.ifpred)
    
    def check_if_predicate(self, ifpred: NodeIfPred):
        if isinstance(ifpred.var, NodeIfPredElif):
            self.check_expression(ifpred.var.expr)
            if (item := self.pop_stack()).type_ not in (BOOL_DEF, INT_DEF):
                self.compiler_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{item.type_}`", item.loc)
            self.check_scope(ifpred.var.scope)
            if ifpred.var.pred is not None:
                self.check_if_predicate(ifpred.var.pred)
        elif isinstance(ifpred.var, NodeIfPredElse): # type: ignore (uses else for error catching)
            self.check_scope(ifpred.var.scope)
        else:
            raise ValueError("Unreachable")
    
    def check_while(self, while_stmt: NodeStmtWhile):
        self.check_expression(while_stmt.expr)
        if (item := self.pop_stack()).type_ not in (BOOL_DEF, INT_DEF):
            self.compiler_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{item.type_}`", item.loc)
        self.check_scope(while_stmt.scope)
    
    def check_do_while(self, do_while_stmt: NodeStmtDoWhile):
        self.check_scope(do_while_stmt.scope)
        self.check_expression(do_while_stmt.expr)
        if (item := self.pop_stack()).type_ not in (BOOL_DEF, INT_DEF):
            self.compiler_error("Type", f"expected type `{BOOL_DEF}` or `{INT_DEF}`, got `{item.type_}`", item.loc)
    
    def check_for(self, for_stmt: NodeStmtFor):
        self.check_decl(for_stmt.ident_def)

        self.check_expression(for_stmt.condition)
        if (item := self.pop_stack()).type_ != BOOL_DEF:
            self.compiler_error("Type", f"expected type `{BOOL_DEF}`, got `{item.type_}`", item.loc)
        
        self.check_scope(for_stmt.scope)

        self.check_reassign(for_stmt.ident_assign)
    
    def check_print(self, print_stmt: NodeStmtPrint):
        self.check_expression(print_stmt.content)
        if (item := self.pop_stack()).type_ not in (CHAR_DEF, STR_DEF):
            self.compiler_error("Type", f"expected type `{CHAR_DEF}` or `{STR_DEF}`, got `{item.type_}`", item.loc)
        print_stmt.cont_type = item.type_
