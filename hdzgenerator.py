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
        """
        returns a name for a new label based on the amount of labels already created
        """
        self.label_count += 1
        return "label" + str(self.label_count)

    def begin_scope(self) -> None:
        """
        only used in the generate_scope() method,
        adds the amount of variables to the scopes list 
        so the end scopes function knows how many variables it should delete
        """
        self.scopes.append(len(self.variables))

    def end_scope(self) -> None:
        """
        only used in the generate_scope() method,
        removes the last scopes variables from memory (by moving the stack pointer),
        removes itself from the generators list of scopes,
        removes the aforementioned variables from the generators dictionary
        """
        pop_count: int = len(self.variables) - self.scopes[-1]

        self.output.append("    add rsp, " + str(pop_count * 8) + "\n")
        self.stack_size -= pop_count
        for _ in range(pop_count):
            self.variables.popitem()
        del self.scopes[-1]

    def generate_term(self, term: prs.NodeTerm) -> None:
        """
        generates a term, a term being a variable or a number
        """
        if isinstance(term.var, prs.NodeTermInt):
            if term.negative:
                term.var.int_lit.value = "-" + term.var.int_lit.value
            self.output.append("    mov rax, " + term.var.int_lit.value + "\n")
            self.push("rax")
        elif isinstance(term.var, prs.NodeTermIdent):
            if term.var.ident.value not in self.variables.keys():
                self.raise_error("Value", f"variable was not declared: {term.var.ident.value}")
            location = self.variables[term.var.ident.value]
            self.push(f"QWORD [rsp + {(self.stack_size - location - 1) * 8}]") # QWORD 64 bits (word = 16 bits)
            if term.negative:
                self.pop("rbx")
                self.output.append("    mov rax, -1\n")
                self.output.append("    mul rbx\n")
                self.push("rax")
        elif isinstance(term.var, prs.NodeTermParen):
            self.generate_expression(term.var.expr)
            if term.negative:
                self.pop("rbx")
                self.output.append("    mov rax, -1\n")
                self.output.append("    mul rbx\n")
                self.push("rax")
    
    def generate_binary_expression(self, bin_expr: prs.NodeBinExpr) -> None:
        """
        generates a binary expression that gets pushed on top of the stack
        """
        if isinstance(bin_expr.var, prs.NodeBinExprAdd):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    add rax, rbx\n")
            self.push("rax")
        elif isinstance(bin_expr.var, prs.NodeBinExprMulti):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    mul rbx\n")
            self.push("rax")
        elif isinstance(bin_expr.var, prs.NodeBinExprSub):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    sub rax, rbx\n")
            self.push("rax")
        elif isinstance(bin_expr.var, prs.NodeBinExprDiv):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    div rbx\n")
            self.push("rax")
        elif isinstance(bin_expr.var, prs.NodeBinExprComp): 
            #TODO: make this generate a value 
            #and handle the comparison instead of leaving that to the if statement block
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
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
        """
        generates the following statements connected to the if statement if there are any
        """
        if isinstance(pred.var, prs.NodeIfPredElif):
            self.output.append("    ;elif\n")
            self.generate_expression(pred.var.expr)
            label = self.create_label()

            if isinstance(pred.var.expr.var.var, prs.NodeBinExprComp):
                self.pop("rax")
                self.pop("rbx")
                self.output.append("    cmp rax, rbx\n")
                if_comparison: str = "jne "
            else:
                print(pred.var.expr.var.var)
                self.pop("rax")
                self.output.append("    test rax, rax\n")
                if_comparison: str = "jz "
            
            self.output.append("    " + if_comparison + label + "\n")
            self.generate_scope(pred.var.scope)
            self.output.append("    jmp " + end_label + "\n")
            self.output.append(label + ":\n")
            self.output.append("    ;/elif\n")
            if pred.var.pred is not None:
                self.generate_if_predicate(pred.var.pred, end_label)

        elif isinstance(pred.var, prs.NodeIfPredElse):
            self.output.append("    ;else\n")
            self.generate_scope(pred.var.scope)
            self.output.append("    ;/else\n")

    def generate_statement(self, statement) -> None:
        """
        generates a statement based on the node given
        """
        if isinstance(statement, prs.NodeStmtExit):
            self.generate_expression(statement.expr)
            self.output.append("    ; manual exit (vychod)\n")
            self.output.append("    mov rax, 60\n")
            self.pop("rdi") # pop gets the top of the stack, puts it into rdi
            self.output.append("    syscall\n")

        elif isinstance(statement, prs.NodeStmtLet):
            if statement.ident.value in self.variables.keys():
                self.raise_error("Syntax", f"variable has been already declared: {statement.ident.value}")
            stack_size_buffer = self.stack_size # stack size changes after generating the expression, thats why its saved here
            self.generate_expression(statement.expr)
            self.variables.update({statement.ident.value : stack_size_buffer})
        
        elif isinstance(statement, prs.NodeScope):
            self.generate_scope(statement)
        
        elif isinstance(statement, prs.NodeStmtIf):
            self.output.append("    ;if block\n")
            self.generate_expression(statement.expr)
            label = self.create_label()

            if isinstance(statement.expr.var.var, prs.NodeBinExprComp):
                self.pop("rax")
                self.pop("rbx")
                self.output.append("    cmp rax, rbx\n")
                if_comparison: str = "jne "
            else:
                self.pop("rax")
                self.output.append("    test rax, rax\n")
                if_comparison: str = "jz "

            self.output.append("    " + if_comparison + label + "\n")
            self.generate_scope(statement.scope)
            
            if statement.ifpred is not None:
                end_label = self.create_label()
                self.output.append("    jmp " + end_label + "\n")
                self.output.append(label + ":\n")
                self.generate_if_predicate(statement.ifpred, end_label)
                self.output.append(end_label + ":\n")
            else:
                self.output.append(label + ":\n")
            self.output.append("    ;/if block\n")

        elif isinstance(statement, prs.NodeStmtAssign):
            self.output.append("    ;reassigning a variable\n")
            if statement.ident.value not in self.variables.keys():
                self.raise_error("Value", "undeclared identifier: " + statement.ident.value)
            
            self.generate_expression(statement.expr)
            self.pop("rax")
            self.output.append(f"    mov [rsp + {(self.stack_size - self.variables[statement.ident.value] - 1) * 8}], rax\n")
            self.output.append("    ;/reassigning a variable\n")

        elif statement == "new_line": # just used for tracking line numbers
            self.line_number += 1

    def generate_program(self) -> str:
        """
        generates the whole assembly based on the nodes that are given,
        returns a string that contains the assembly
        """
        self.output.append("global _start\n_start:\n")
        for stmt in self.main_program.stmts:
            self.generate_statement(stmt)
        self.output.append("    ; default exit\n    mov rax, 60\n    mov rdi, 0\n    syscall" )
        return "".join(self.output)
