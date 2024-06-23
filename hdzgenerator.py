from hdzlexer import Token
from hdzerrors import raise_error
import hdzparser as prs
import hdztokentypes as tt


class Generator:
    def __init__(self, program: prs.NodeProgram, file: str) -> None:
        self.main_program: prs.NodeProgram = program
        self.output: str = "" #TODO: make this a list, concatenating strings takes too long
        
        self.file: str = file
        self.line_index: int = 1
        
        self.stack_size: int = 0
        self.variables: dict = {}
    
    def push(self, register: str):
        self.output += "    push " + register + "\n"
        self.stack_size += 1

    def pop(self, register: str):
        self.output += "    pop " + register + "\n"
        self.stack_size -= 1

    def generate_expression(self, expression: prs.NodeExpr) -> None:
        """
        generates an expression and pushes it on top of the stack
        """
        if isinstance(expression.var, prs.NodeExprInt):
            self.output += "    mov rax, " + expression.var.int_lit.value + "\n"
            self.push("rax")
        elif isinstance(expression.var, prs.NodeExprIdent):
            if expression.var.ident.value not in self.variables.keys():
                raise_error("Value", f"variable was not declared: {expression.var.ident.value}", 
                            self.file, self.line_index)
            location = self.variables[expression.var.ident.value]
            self.push(f"QWORD [rsp + {(self.stack_size - location - 1) * 8}]") # QWORD 64 bits (word = 16 bits)

    def generate_statement(self, statement) -> None:
        if isinstance(statement, prs.NodeStmtExit):
            self.generate_expression(statement.expr)
            self.output += "    ; manual exit (vychod)\n"
            self.output += "    mov rax, 60\n"
            self.pop("rdi") # pop gets the top of the stack, puts it into rdi
            self.output += "    syscall\n"

        elif isinstance(statement, prs.NodeStmtLet):
            if statement.ident.value in self.variables.keys():
                raise_error("Syntax", f"variable has been already declared: {statement.ident.value}", 
                            self.file, self.line_index)
            self.variables.update({statement.ident.value : self.stack_size})
            self.generate_expression(statement.expr)

    def generate_program(self) -> str: 
        self.output: str = "global _start\n_start:\n"
        for stmt in self.main_program.stmts:
            self.generate_statement(stmt)
            self.line_index += 1
        self.output += """
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall"""
        return self.output