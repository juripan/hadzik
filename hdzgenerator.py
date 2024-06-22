from hdzlexer import Token
from hdzparser import NodeProgram, NodeExit
import token_types as tt


class Generator:
    def __init__(self, node: NodeProgram) -> None:
        self.main_node = node

    def generate(self) -> str:
        res: str = "global _start\n_start:\n"
        for stmt in self.main_node.stmts:
            if isinstance(stmt, NodeExit):
                res += "    mov rax, 60\n"
                res += "    mov rdi, " + stmt.node_expr.var.number.value + "\n"
                res += "    syscall\n"
        res += """
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall"""
        return res