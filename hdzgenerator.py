from hdzerrors import ErrorHandler
import hdzparser as prs
from collections import OrderedDict


class Generator(ErrorHandler):
    def __init__(self, program: prs.NodeProgram, file_content: str) -> None:
        super().__init__(file_content)
        self.main_program: prs.NodeProgram = program
        self.output: list = []

        self.column_number = -1
        
        self.stack_size: int = 0 # uses whole 64bit integers as size (until more datatypes are added)
        self.variables: OrderedDict = OrderedDict()
        self.scopes: list[int] = []
        self.label_count: int = 0
    
    def push(self, register: str):
        """
        adds a push instruction to the output and updates the stack size 
        """
        self.output.append("    push " + register + "\n")
        self.stack_size += 1

    def pop(self, register: str):
        """
        adds a pop instruction to the output and updates the stack size 
        """
        self.output.append("    pop " + register + "\n")
        self.stack_size -= 1

    def create_label(self) -> str:
        self.label_count += 1
        return "label" + str(self.label_count)

    def begin_scope(self):
        self.scopes.append(len(self.variables))

    def end_scope(self):
        pop_count: int = len(self.variables) - self.scopes[-1]

        self.output.append("    ; scope end\n    add rsp, " + str(pop_count * 8) + "\n")
        self.stack_size -= pop_count
        for _ in range(pop_count):
            self.variables.popitem()
        del self.scopes[-1]

    def generate_term(self, term: prs.NodeTerm) -> None:
        if isinstance(term.var, prs.NodeTermInt):
            self.output.append("    ; integer eval\n    mov rax, " + term.var.int_lit.value + "\n")
            self.push("rax")
        elif isinstance(term.var, prs.NodeTermIdent):
            if term.var.ident.value not in self.variables.keys():
                self.raise_error("Value", f"variable was not declared: {term.var.ident.value}")
            location = self.variables[term.var.ident.value]
            self.output.append("    ; identifier eval\n")
            self.push(f"QWORD [rsp + {(self.stack_size - location - 1) * 8}]") # QWORD 64 bits (word = 16 bits)
        elif isinstance(term.var, prs.NodeTermParen):
            self.generate_expression(term.var.expr)
    
    def generate_binary_expression(self, bin_expr: prs.NodeBinExpr) -> None:
        if isinstance(bin_expr.var, prs.NodeBinExprAdd):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.output.append("    ; adding\n")
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    add rax, rbx\n")
            self.push("rax")
        elif isinstance(bin_expr.var, prs.NodeBinExprMulti):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.output.append("    ; multiplying\n")
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    mul rbx\n")
            self.push("rax")
        elif isinstance(bin_expr.var, prs.NodeBinExprSub):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.output.append("    ; subtracting\n")
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    sub rax, rbx\n")
            self.push("rax")
        elif isinstance(bin_expr.var, prs.NodeBinExprDiv):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.output.append("    ; dividing\n")
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    div rbx\n")
            self.push("rax")
        else:
            self.raise_error("Generator", "failed to parse binary expression")

    def generate_expression(self, expression: prs.NodeExpr) -> None:
        """
        generates an expression and pushes it on top of the stack
        """
        if isinstance(expression.var, prs.NodeTerm):
            self.generate_term(expression.var)
        elif isinstance(expression.var, prs.NodeBinExpr):
            self.generate_binary_expression(expression.var)

    def generate_scope(self, scope: prs.NodeScope) -> None:
        self.begin_scope()
        for stmt in scope.stmts:
            self.generate_statement(stmt)
        self.end_scope()

    def generate_if_predicate(self, pred: prs.NodeIfPred, end_label: str) -> None:
        if isinstance(pred.var, prs.NodeIfPredElif):
            self.generate_expression(pred.var.expr)
            self.pop("rax")
            label = self.create_label()
            self.output.append("    test rax, rax\n")
            self.output.append("    jz " + label + "\n")
            self.generate_scope(pred.var.scope)
            self.output.append("    jmp " + end_label + "\n")
            self.output.append(label + ":\n")
            if pred.var.pred is not None:
                self.generate_if_predicate(pred.var.pred, end_label)

        elif isinstance(pred.var, prs.NodeIfPredElse):
            self.generate_scope(pred.var.scope)

    def generate_statement(self, statement) -> None:
        if isinstance(statement, prs.NodeStmtExit):
            self.generate_expression(statement.expr)
            self.output.append("    ; manual exit (vychod)\n")
            self.output.append("    mov rax, 60\n")
            self.pop("rdi") # pop gets the top of the stack, puts it into rdi
            self.output.append("    syscall\n")

        elif isinstance(statement, prs.NodeStmtLet):
            if statement.ident.value in self.variables.keys():
                self.raise_error("Syntax", f"variable has been already declared: {statement.ident.value}")
            self.variables.update({statement.ident.value : self.stack_size})
            self.generate_expression(statement.expr)
        
        elif isinstance(statement, prs.NodeScope):
            self.generate_scope(statement)
        
        elif isinstance(statement, prs.NodeStmtIf):
            self.generate_expression(statement.expr)
            self.pop("rax")
            label = self.create_label()
            self.output.append("    test rax, rax\n")
            self.output.append("    jz " + label + "\n")
            self.generate_scope(statement.scope)
            if statement.ifpred is not None:
                end_label = self.create_label()
                self.output.append("    jmp " + end_label + "\n")
                self.output.append(label + ":\n")
                self.generate_if_predicate(statement.ifpred, end_label)
                self.output.append(end_label + ":\n")
            else:
                self.output.append(label + ":\n")

        elif isinstance(statement, prs.NodeStmtAssign):
            if statement.ident.value not in self.variables.keys():
                self.raise_error("Value", "undeclared identifier: " + statement.ident.value)
            
            expr = self.generate_expression(statement.expr)
            self.pop("rax")
            self.output.append(f"    mov [rsp + {(self.stack_size - self.variables[statement.ident.value] - 1) * 8}], rax\n")


        elif statement == "new_line": # just used for tracking line numbers
            self.line_number += 1

    def generate_program(self) -> str:
        self.output.append("global _start\n_start:\n")
        for stmt in self.main_program.stmts:
            self.generate_statement(stmt)
        self.output.append("    ; default exit\n    mov rax, 60\n    mov rdi, 0\n    syscall" )
        return "".join(self.output)
