from hdzlexer import Token
from hdzerrors import ErrorHandler
import hdzparser as prs
import hdztokentypes as tt


class Generator(ErrorHandler):
    def __init__(self, program: prs.NodeProgram, file_content: str) -> None:
        super().__init__(file_content)
        self.main_program: prs.NodeProgram = program
        self.output: list = []
        
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

    def generate_expression(self, expression: prs.NodeExpr) -> None:
        """
        generates an expression and pushes it on top of the stack
        """
        if isinstance(expression.var, prs.NodeExprInt):
            self.output.append("    ; integer eval\n    mov rax, " + expression.var.int_lit.value + "\n")
            self.push("rax")
        elif isinstance(expression.var, prs.NodeExprIdent):
            if expression.var.ident.value not in self.variables.keys():
                self.raise_error("Value", f"variable was not declared: {expression.var.ident.value}",
                                 ignores_whitespace=True)
            location = self.variables[expression.var.ident.value]
            self.output.append("    ; identifier eval\n")
            self.push(f"QWORD [rsp + {(self.stack_size - location - 1) * 8}]") # QWORD 64 bits (word = 16 bits)

    def generate_statement(self, statement) -> None:
        if isinstance(statement, prs.NodeStmtExit):
            self.generate_expression(statement.expr)
            self.output.append("    ; manual exit (vychod)\n")
            self.output.append("    mov rax, 60\n")
            self.pop("rdi") # pop gets the top of the stack, puts it into rdi
            self.output.append("    syscall\n")

        elif isinstance(statement, prs.NodeStmtLet):
            if statement.ident.value in self.variables.keys():
                self.raise_error("Syntax", f"variable has been already declared: {statement.ident.value}", 
                                 ignores_whitespace=True)
            self.variables.update({statement.ident.value : self.stack_size})
            self.generate_expression(statement.expr)

    def generate_program(self) -> str: 
        self.output.append("global _start\n_start:\n")
        for stmt in self.main_program.stmts:
            self.line_number += 1
            self.generate_statement(stmt)
        self.output.append("    ; default exit\n    mov rax, 60\n    mov rdi, 0\n    syscall" )
        return "".join(self.output)