from hdzerrors import ErrorHandler
import hdzparser as prs
#TODO: maybe use numpy arrays instead of python lists, maybe

class Generator(ErrorHandler):
    def __init__(self, program: prs.NodeProgram, file_content: str) -> None:
        super().__init__(file_content)
        self.main_program: prs.NodeProgram = program
        self.output: list = []

        self.column_number = -1
        
        self.stack_size: int = 0 # uses whole 64bit integers as size (until more datatypes are added)
        self.variables: dict = {}
    
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
    
    def generate_binary_expression(self, bin_expr: prs.NodeBinExpr):
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
        
        elif statement is None: # just used for tracking line numbers
            self.line_number += 1

    def generate_program(self) -> str: 
        self.output.append("global _start\n_start:\n")
        for stmt in self.main_program.stmts:
            self.generate_statement(stmt)
        self.output.append("    ; default exit\n    mov rax, 60\n    mov rdi, 0\n    syscall" )
        return "".join(self.output)
