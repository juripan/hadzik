from hdzerrors import ErrorHandler
import hdzparser as prs
from collections import OrderedDict
import hdztokentypes as tt


class Generator(ErrorHandler):
    def __init__(self, program: prs.NodeProgram, file_content: str) -> None:
        super().__init__(file_content)
        self.main_program: prs.NodeProgram = program
        self.output: list = []

        self.column_number = -1
        
        self.stack_size: int = 0 # uses whole 64bit integers as size (until more datatypes are added)
        self.variables: OrderedDict[str, tuple[int, str, int]] = OrderedDict() #tuples content is location and word size and size in bytes
        self.scopes: list[int] = []
        self.label_count: int = 0
        self.loop_end_labels: list[str] = []
        self.data_section_index: int = 1
        self.bss_section_index: int = 2

        self.registers_64bit: tuple[str] = ("rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rsp", "rbp", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15")
        self.registers_16bit: tuple[str] = ("ax", "bx", "cx", "dx", "si", "di", "sp", "bp", "r8w", "r9w", "r10w", "r11w", "r12w", "r13w", "r14w", "r15w")
    
    def push(self, content: str):
        """
        adds a push instruction to the output and updates the stack size 
        """
        #NOTE: size in bytes
        if content in self.registers_64bit or content.startswith("QWORD"): #TODO: add proper size to the stack size pointer
            size = 8
        elif content in self.registers_16bit or content.startswith("WORD"):
            size = 2
        self.output.append("    push " + content + "\n")
        self.stack_size += 1

    def pop(self, content: str):
        """
        adds a pop instruction to the output and updates the stack size 
        """
        self.output.append("    pop " + content + "\n")
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
        generates a term, a term being a variable or a number, 
        gets pushed on to of the stack
        """
        if isinstance(term.var, prs.NodeTermInt):
            if term.negative:
                term.var.int_lit.value = "-" + term.var.int_lit.value
            self.push(term.var.int_lit.value) #NOTE: this is possible if the value is the size of 4bits or less, if more you have to push it onto a stack first
        elif isinstance(term.var, prs.NodeTermIdent):
            if term.var.ident.value not in self.variables.keys():
                self.raise_error("Value", f"variable was not declared: {term.var.ident.value}")
            location = self.variables[term.var.ident.value][0]
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
        elif isinstance(term.var, prs.NodeTermNot):
            self.generate_term(term.var.term)
            self.pop("rbx")
            self.output.append("    xor eax, eax\n")
            self.output.append("    test rbx, rbx\n")
            self.output.append("    sete al\n")
            self.output.append("    movzx rax, al\n")
            self.push("rax")
    
    def generate_comparison_expression(self, comparison: prs.NodeBinExprComp) -> None:
        """
        generates a comparison expression,
        type of binary expression that returns 1 or 0 depending on if its true or false
        """
        self.generate_expression(comparison.rhs)
        self.generate_expression(comparison.lhs)
        self.pop("rax")
        self.pop("rbx")
        self.output.append("    cmp rax, rbx\n")
        if comparison.comp_sign.type == tt.is_equal:
            self.output.append("    sete al\n")
        elif comparison.comp_sign.type == tt.is_not_equal:
            self.output.append("    setne al\n")
        elif comparison.comp_sign.type == tt.larger_than:
            self.output.append("    setg al\n")
        elif comparison.comp_sign.type == tt.less_than:
            self.output.append("    setl al\n")
        elif comparison.comp_sign.type == tt.larger_than_or_eq:
            self.output.append("    setge al\n")
        elif comparison.comp_sign.type == tt.less_than_or_eq:
            self.output.append("    setle al\n")
        else:
            self.raise_error("Syntax", "Invalid comparison expression")
        self.output.append("    movzx rax, al\n")
        self.push("rax")

    def generate_logical_expression(self, logic_expr: prs.NodeBinExprLogic) -> None:
        """
        generates an eval for a logical expression (AND or OR),
        its result can be either 1 or 0
        """
        self.generate_expression(logic_expr.rhs)
        self.generate_expression(logic_expr.lhs)
        self.pop("rax")
        self.pop("rbx")
        self.output.append("    mov rcx, rax\n")
        self.output.append("    test rbx, rbx\n")
        if logic_expr.logical_operator.type == tt.and_:
            self.output.append("    cmovz rcx, rbx\n")
        elif logic_expr.logical_operator.type == tt.or_:
            self.output.append("    cmovnz rcx, rbx\n")
        else:
            self.raise_error("Syntax", "Invalid logic expression")
        self.output.append("    test rcx, rcx\n")
        self.output.append("    setne al\n")
        self.output.append("    movzx rax, al\n")
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
            self.output.append("    idiv rbx\n") #NOTE: idiv is used because div only works with unsigned numbers
            self.push("rax")
        elif isinstance(bin_expr.var, prs.NodeBinExprMod):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    mov rdx, 0\n")
            self.output.append("    cqo\n") # sign extends so the modulus result can be negative
            self.output.append("    idiv rbx\n")
            self.push("rdx") # assembly stores the modulus in rdx after the standard division instruction
        elif isinstance(bin_expr.var, prs.NodeBinExprComp): 
            self.generate_comparison_expression(bin_expr.var)
        elif isinstance(bin_expr.var, prs.NodeBinExprLogic):
            self.generate_logical_expression(bin_expr.var)
        else:
            self.raise_error("Generator", "failed to generate binary expression")

    def generate_expression(self, expression: prs.NodeExpr) -> None:
        """
        generates an expression and pushes it on top of the stack
        """
        if isinstance(expression.var, prs.NodeTerm):
            self.generate_term(expression.var)
        elif isinstance(expression.var, prs.NodeBinExpr):
            self.generate_binary_expression(expression.var)
    
    def generate_char(self, char: prs.NodeTermChar) -> None:
        self.push(char.char.value)

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

            self.pop("rax")
            self.output.append("    test rax, rax\n")
            
            self.output.append("    jz " + label + "\n")
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

    def generate_let(self, let_stmt: prs.NodeStmtLet):
        if let_stmt.ident.value in self.variables.keys():
            self.raise_error("Syntax", f"variable has been already declared: {let_stmt.ident.value}")
        stack_size_buffer: int = self.stack_size # stack size changes after generating the expression, thats why its saved here
        var_size: str = "QWORD"
        byte_size: int = 8
        self.generate_expression(let_stmt.expr)
        self.variables.update({let_stmt.ident.value : (stack_size_buffer, var_size, byte_size)})

    def generate_reassign(self, reassign_stmt: prs.NodeStmtReassign):
        self.output.append("    ;reassigning a variable\n")
        if isinstance(reassign_stmt.var, prs.NodeStmtReassignEq):
            if reassign_stmt.var.ident.value not in self.variables.keys():
                self.raise_error("Value", "undeclared identifier: " + reassign_stmt.var.ident.value)
            self.generate_expression(reassign_stmt.var.expr)
            self.pop("rax")
            location, _, byte_size = self.variables[reassign_stmt.var.ident.value]
            self.output.append(f"    mov [rsp + {(self.stack_size - location - 1) * byte_size}], rax\n")
        elif isinstance(reassign_stmt.var, (prs.NodeStmtReassignInc, prs.NodeStmtReassignDec)):
            if reassign_stmt.var.ident.value not in self.variables.keys():
                self.raise_error("Value", "undeclared identifier: " + reassign_stmt.var.ident.value)
            location, size, byte_size = self.variables[reassign_stmt.var.ident.value]
            self.push(f"{size} [rsp + {(self.stack_size - location - 1) * byte_size}]") # QWORD 64 bits (word = 16 bits)
            self.pop("rax")
            self.output.append("    inc rax\n" 
                               if isinstance(reassign_stmt.var, prs.NodeStmtReassignInc) 
                               else "    dec rax\n")
            self.output.append(f"    mov [rsp + {(self.stack_size - location - 1) * byte_size}], rax\n")
        self.output.append("    ;/reassigning a variable\n")

    def generate_exit(self, exit_stmt: prs.NodeStmtExit) -> None:
        self.generate_expression(exit_stmt.expr)
        self.output.append("    ; manual exit (vychod)\n")
        self.output.append("    mov rax, 60\n")
        self.pop("rdi")
        self.output.append("    syscall\n")

    def generate_if_statement(self, if_stmt: prs.NodeStmtIf) -> None:
        self.output.append("    ;if block\n")
        self.generate_expression(if_stmt.expr)
        label = self.create_label()

        self.pop("rax")
        self.output.append("    test rax, rax\n")

        self.output.append("    jz " + label + "\n")
        self.generate_scope(if_stmt.scope)
        
        if if_stmt.ifpred is not None:
            end_label = self.create_label()
            self.output.append("    jmp " + end_label + "\n")
            self.output.append(label + ":\n")
            self.generate_if_predicate(if_stmt.ifpred, end_label)
            self.output.append(end_label + ":\n")
        else:
            self.output.append(label + ":\n")
        self.output.append("    ;/if block\n")

    def generate_while(self, while_stmt: prs.NodeStmtWhile) -> None:
        self.output.append("    ;while loop\n")
        end_label = self.create_label()
        reset_label = self.create_label()
        self.loop_end_labels.append(end_label)

        self.output.append(reset_label  + ":\n")

        self.generate_expression(while_stmt.expr)
        self.pop("rax")
        self.output.append("    test rax, rax\n")
        self.output.append(f"    jz {end_label}\n")

        self.generate_scope(while_stmt.scope)
        
        self.output.append("    jmp " + reset_label + "\n")
        self.output.append(end_label  + ":\n")
        self.output.append("    ;/while loop\n")
        self.loop_end_labels.pop()

    def generate_do_while(self, do_while_stmt: prs.NodeStmtDoWhile) -> None:
        self.output.append("    ;do while loop\n")
        end_label = self.create_label()
        reset_label = self.create_label()
        self.loop_end_labels.append(end_label)

        self.output.append(reset_label  + ":\n")

        self.generate_scope(do_while_stmt.scope)

        self.generate_expression(do_while_stmt.expr)
        self.pop("rax")
        self.output.append("    test rax, rax\n")
        self.output.append(f"    jz {end_label}\n")

        self.output.append("    jmp " + reset_label + "\n")
        self.output.append(end_label  + ":\n")
        self.output.append("    ;/do while loop\n")
        self.loop_end_labels.pop()

    def generate_for(self, for_stmt: prs.NodeStmtFor) -> None:
        self.output.append("    ;for loop\n")
        end_label = self.create_label()
        reset_label = self.create_label()
        self.loop_end_labels.append(end_label)

        self.generate_let(for_stmt.ident_def)

        self.output.append(reset_label  + ":\n")

        self.generate_comparison_expression(for_stmt.condition)
        
        self.pop("rax")
        self.output.append("    test rax, rax\n")
        self.output.append(f"    jz {end_label}\n")

        self.generate_scope(for_stmt.scope)
        
        self.generate_reassign(for_stmt.ident_assign)

        self.output.append("    jmp " + reset_label + "\n")
        self.output.append(end_label  + ":\n")
        self.output.append("    add rsp, " + str(8) + "\n")
        self.stack_size -= 1 # does this to remove the variable after the i loop ends
        self.variables.popitem()
        self.output.append("    ;/for loop\n")
        self.loop_end_labels.pop()

    def generate_print(self, print_stmt: prs.NodeStmtPrint) -> None:
        init_stack_size = self.stack_size
        if isinstance(print_stmt.content, prs.NodeExpr):
            self.generate_expression(print_stmt.content)
        elif isinstance(print_stmt.content, prs.NodeTermChar):
            self.generate_char(print_stmt.content)
        expr_loc = f"rsp"
        self.output.append("    ; printing\n")
        self.output.append("    mov rax, 1\n")
        self.output.append("    mov rdi, 1\n")
        self.output.append(f"    mov rsi, {expr_loc}\n")
        self.output.append("    mov rdx, 1\n")
        self.output.append("    syscall\n")
        pushed_res = self.stack_size - init_stack_size #it removes the printed expression because it causes a mess in the stack when looping
        self.output.append("    add rsp, " + str(pushed_res * 8) + "\n") #removes the printed expression from the stack
        self.stack_size -= 1 #lowers the stack size
        self.output.append("    ; /printing\n")

    def generate_statement(self, statement: prs.NodeStmt) -> None:
        """
        generates a statement based on the node given
        """
        if isinstance(statement.stmt_var, prs.NodeStmtExit):
            self.generate_exit(statement.stmt_var)

        elif isinstance(statement.stmt_var, prs.NodeStmtLet):
            self.generate_let(statement.stmt_var)
        
        elif isinstance(statement.stmt_var, prs.NodeScope):
            self.generate_scope(statement.stmt_var)
        
        elif isinstance(statement.stmt_var, prs.NodeStmtIf):
            self.generate_if_statement(statement.stmt_var)

        elif isinstance(statement.stmt_var, prs.NodeStmtReassign):
            self.generate_reassign(statement.stmt_var)

        elif isinstance(statement.stmt_var, prs.NodeStmtWhile):
            self.generate_while(statement.stmt_var)
        
        elif isinstance(statement.stmt_var, prs.NodeStmtDoWhile):
            self.generate_do_while(statement.stmt_var)
        
        elif isinstance(statement.stmt_var, prs.NodeStmtFor):
            self.generate_for(statement.stmt_var)
        
        elif isinstance(statement.stmt_var, prs.NodeStmtPrint):
            self.generate_print(statement.stmt_var)

        elif isinstance(statement.stmt_var, prs.NodeStmtBreak):
            print(self.loop_end_labels)
            if self.loop_end_labels:
                self.output.append("    ; break \n")
                self.output.append("    jmp " + self.loop_end_labels[-1] + "\n")
            else:
                self.raise_error("Syntax", "cant break out of a loop when not inside one")

        elif statement.stmt_var == "new_line": # just used for tracking line numbers TODO: fix line number tracking in generator
            self.line_number += 1

    def generate_program(self) -> str:
        """
        generates the whole assembly based on the nodes that are given,
        returns a string that contains the assembly
        """
        self.output.append("section .data\n")
        self.output.append("section .bss\n")
        self.output.append("section .text\n    global _start\n")
        self.output.append("_start:\n")
        for stmt in self.main_program.stmts:
            self.generate_statement(stmt)
        self.output.append("    ; default exit\n    mov rax, 60\n    mov rdi, 0\n    syscall" )
        return "".join(self.output)
