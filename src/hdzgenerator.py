from collections import OrderedDict

from hdzerrors import ErrorHandler
from comptypes import *
import hdztokentypes as tt


class Generator(ErrorHandler):
    def __init__(self, program: NodeProgram, file_content: str) -> None:
        super().__init__(file_content)
        self.main_program: NodeProgram = program
        self.output: list[str] = []

        self.column_number = -1
        
        self.stack_size: int = 0 # uses whole 8 bytes (half of a word) as a unit
        self.stack_item_sizes: list[int] = [] # same as above

        self.variables: OrderedDict[str, tuple[int, str, int]] = OrderedDict() #tuples content is location and word size and size in bytes
        self.scopes: list[int] = []
        
        self.label_count: int = 0
        self.loop_end_labels: list[str] = []
        
        self.data_section_index: int = 1
        self.bss_section_index: int = 2

        self.registers_64bit: tuple[str, 16] = ("rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rsp", "rbp", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15")
        self.registers_16bit: tuple[str, 16] = ("ax", "bx", "cx", "dx", "si", "di", "sp", "bp", "r8w", "r9w", "r10w", "r11w", "r12w", "r13w", "r14w", "r15w")
    
    def push(self, content: str):
        """
        adds a push instruction to the output and updates the stack size 
        """
        #NOTE: size in bytes
        if content in self.registers_64bit or content.startswith("QWORD"):
            size = 8
        elif content in self.registers_16bit or content.startswith("WORD"):
            size = 2
        else:
            raise ValueError("invalid register")
        self.output.append("    push " + content + "\n")
        self.stack_size += size
        self.stack_item_sizes.append(size)
        print("push", self.stack_size, self.stack_item_sizes, self.variables)

    def pop(self, content: str):
        """
        adds a pop instruction to the output and updates the stack size 
        """
        self.output.append("    pop " + content + "\n")
        self.stack_size -= self.stack_item_sizes.pop() # removes and gives the last number
        print("pop", self.stack_size, self.stack_item_sizes, self.variables)

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
        returns prematurely if theres nothing to remove
        """
        pop_count: int = len(self.variables) - self.scopes[-1]
        if pop_count == 0:
            return # nothing to remove, if its not here then slice accepts all of the stack -> list[0:] == list

        popped_size: int = sum(self.stack_item_sizes[-pop_count:])
        self.output.append("    add rsp, " + str(popped_size) + "\n")
        self.stack_size -= popped_size
        for _ in range(pop_count):
            self.variables.popitem()
            self.stack_item_sizes.pop()
        del self.scopes[-1]

    def generate_boolean(self, bool: NodeTermBool) -> None:
        self.output.append(f"    mov ax, {bool.bool.value}\n")
        self.push("ax")

    def generate_term(self, term: NodeTerm) -> None:
        """
        generates a term, a term being a variable or a number, 
        gets pushed on to of the stack
        """
        print(term.var)
        if isinstance(term.var, NodeTermInt):
            if term.negative:
                term.var.int_lit.value = "-" + term.var.int_lit.value
            self.output.append(f"    mov rax, {term.var.int_lit.value}\n")
            self.push("rax")
        elif isinstance(term.var, NodeTermIdent):
            if term.var.ident.value not in self.variables.keys():
                self.raise_error("Value", f"variable was not declared: {term.var.ident.value}", term.var.ident)
            location, word_size, byte_size = self.variables[term.var.ident.value]
            self.push(f"{word_size} [rsp + {self.stack_size - location - byte_size}]") # QWORD 64 bits (word = 16 bits)
            if term.negative:
                self.pop("rbx")
                self.output.append("    mov rax, -1\n")
                self.output.append("    mul rbx\n")
                self.push("rax")
        elif isinstance(term.var, NodeTermBool):
            self.output.append(f"    mov ax, {term.var.bool.value}\n")
            self.push("ax")
        elif isinstance(term.var, NodeTermParen):
            self.generate_expression(term.var.expr)
            if term.negative:
                self.pop("rbx")
                self.output.append("    mov rax, -1\n")
                self.output.append("    mul rbx\n")
                self.push("rax")
        elif isinstance(term.var, NodeTermNot):
            self.generate_term(term.var.term)
            self.pop("rbx")
            self.output.append("    xor eax, eax\n")
            self.output.append("    test rbx, rbx\n")
            self.output.append("    sete al\n")
            self.output.append("    movzx rax, al\n")
            self.push("rax")
    
    def generate_comparison_expression(self, comparison: NodeBinExprComp) -> None:
        """
        generates a comparison expression that pushes a 16bit value onto the stack,
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
            self.raise_error("Syntax", "Invalid comparison expression", comparison.comp_sign)
        #self.output.append("    movzx rax, al\n")
        self.push("ax")

    def generate_binary_logical_expression(self, logic_expr: NodeBinExprLogic) -> None: #TODO: rename ths mess
        """
        generates an eval for a logical expression (AND or OR) that pushes a 16bit value onto the stack,
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
            self.raise_error("Syntax", "Invalid logic expression", logic_expr.logical_operator)
        self.output.append("    test rcx, rcx\n")
        self.output.append("    setne al\n")
        #self.output.append("    movzx rax, al\n")
        self.push("ax")

    def generate_binary_expression(self, bin_expr: NodeBinExpr) -> None:
        """
        generates a binary expression that gets pushed on top of the stack
        """
        if isinstance(bin_expr.var, NodeBinExprAdd):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    add rax, rbx\n")
            self.push("rax")
        elif isinstance(bin_expr.var, NodeBinExprMulti):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    mul rbx\n")
            self.push("rax")
        elif isinstance(bin_expr.var, NodeBinExprSub):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    sub rax, rbx\n")
            self.push("rax")
        elif isinstance(bin_expr.var, NodeBinExprDiv):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    idiv rbx\n") #NOTE: idiv is used because div only works with unsigned numbers
            self.push("rax")
        elif isinstance(bin_expr.var, NodeBinExprMod):
            self.generate_expression(bin_expr.var.rhs)
            self.generate_expression(bin_expr.var.lhs)
            self.pop("rax")
            self.pop("rbx")
            self.output.append("    mov rdx, 0\n")
            self.output.append("    cqo\n") # sign extends so the modulus result can be negative
            self.output.append("    idiv rbx\n")
            self.push("rdx") # assembly stores the modulus in rdx after the standard division instruction
        else:
            self.raise_error("Generator", "failed to generate binary expression")

    def generate_logical_expression(self, expression: NodeLogicExpr):
        if isinstance(expression.var, NodeBinExprComp): 
            self.generate_comparison_expression(expression.var)
        elif isinstance(expression.var, NodeBinExprLogic):
            self.generate_binary_logical_expression(expression.var)

    def generate_expression(self, expression: NodeExpr) -> None:
        """
        generates an expression and pushes it on top of the stack
        """
        if isinstance(expression.var, NodeTerm):
            self.generate_term(expression.var)
        elif isinstance(expression.var, NodeBinExpr):
            self.generate_binary_expression(expression.var)
        elif isinstance(expression.var, NodeLogicExpr):
            self.generate_logical_expression(expression.var)
    
    def generate_char(self, char: NodeTermChar) -> None:
        self.output.append(f"    mov rax, {char.char.value}\n")
        self.push("rax")

    def generate_scope(self, scope: NodeScope) -> None:
        self.begin_scope()
        for stmt in scope.stmts:
            self.generate_statement(stmt)
        self.end_scope()

    def generate_if_predicate(self, pred: NodeIfPred, end_label: str) -> None:
        """
        generates the following statements connected to the if statement if there are any
        """
        if isinstance(pred.var, NodeIfPredElif):
            self.output.append("    ;elif\n")
            self.generate_expression(pred.var.expr)
            label = self.create_label()

            self.pop("ax")
            self.output.append("    test ax, ax\n")
            
            self.output.append("    jz " + label + "\n")
            self.generate_scope(pred.var.scope)
            self.output.append("    jmp " + end_label + "\n")
            self.output.append(label + ":\n")
            self.output.append("    ;/elif\n")
            if pred.var.pred is not None:
                self.generate_if_predicate(pred.var.pred, end_label)

        elif isinstance(pred.var, NodeIfPredElse):
            self.output.append("    ;else\n")
            self.generate_scope(pred.var.scope)
            self.output.append("    ;/else\n")

    def generate_let(self, let_stmt: NodeStmtLet):
        if let_stmt.ident.value in self.variables.keys():
            self.raise_error("Syntax", f"variable has been already declared: {let_stmt.ident.value}", curr_token=let_stmt.ident)
        location: int = self.stack_size # stack size changes after generating the expression, thats why its saved here

        if let_stmt.type_.type == tt.let:
            var_size: str = "QWORD"
            byte_size: int = 8
            if isinstance(let_stmt.expr.var, NodeLogicExpr):
                self.raise_error("Unexpected", "what ")
            self.generate_expression(let_stmt.expr)
        elif let_stmt.type_.type == tt.bool_def:
            var_size: str = "WORD"
            byte_size: int = 2
            if isinstance(let_stmt.expr.var, NodeBinExpr):
                self.raise_error("Unexpected", "what ")
            self.generate_expression(let_stmt.expr)
        else:
            assert False
        
        self.variables.update({let_stmt.ident.value : (location, var_size, byte_size)})

    def generate_reassign(self, reassign_stmt: NodeStmtReassign):
        self.output.append("    ;reassigning a variable\n")
        if reassign_stmt.var.ident.value not in self.variables.keys():
            self.raise_error("Value", "undeclared identifier: " + reassign_stmt.var.ident.value, reassign_stmt.var.ident)
        
        if isinstance(reassign_stmt.var, NodeStmtReassignEq):
            self.generate_expression(reassign_stmt.var.expr)
            self.pop("rax")
            location, _, byte_size = self.variables[reassign_stmt.var.ident.value]
            self.output.append(f"    mov [rsp + {self.stack_size - location - byte_size}], rax\n")
        elif isinstance(reassign_stmt.var, (NodeStmtReassignInc, NodeStmtReassignDec)):
            location, size, byte_size = self.variables[reassign_stmt.var.ident.value]
            self.push(f"{size} [rsp + {self.stack_size - location - byte_size}]") # QWORD 64 bits (word = 16 bits)
            self.pop("rax")
            self.output.append("    inc rax\n" 
                                if isinstance(reassign_stmt.var, NodeStmtReassignInc) 
                                else "    dec rax\n")
            self.output.append(f"    mov [rsp + {self.stack_size - location - byte_size}], rax\n")
        self.output.append("    ;/reassigning a variable\n")

    def generate_exit(self, exit_stmt: NodeStmtExit) -> None:
        self.generate_expression(exit_stmt.expr)
        self.output.append("    ; manual exit (vychod)\n")
        self.output.append("    mov rax, 60\n")
        self.pop("rdi")
        self.output.append("    syscall\n")

    def generate_if_statement(self, if_stmt: NodeStmtIf) -> None:
        self.output.append("    ;if block\n")
        self.generate_expression(if_stmt.expr)
        label = self.create_label()

        self.pop("ax") #TODO: make the comparison expressions use the correct size depending on type (if not used it mis-aligns the stack cuz when popping into rax it takes the top 64bits and cuts off a value misaliging the sack)
        self.output.append("    test ax, ax\n")

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

    def generate_while(self, while_stmt: NodeStmtWhile) -> None:
        self.output.append("    ;while loop\n")
        end_label = self.create_label()
        reset_label = self.create_label()
        self.loop_end_labels.append(end_label)

        self.output.append(reset_label  + ":\n")

        self.generate_expression(while_stmt.expr)
        self.pop("ax")
        self.output.append("    test ax, ax\n")
        self.output.append(f"    jz {end_label}\n")

        self.generate_scope(while_stmt.scope)
        
        self.output.append("    jmp " + reset_label + "\n")
        self.output.append(end_label  + ":\n")
        self.output.append("    ;/while loop\n")
        self.loop_end_labels.pop()

    def generate_do_while(self, do_while_stmt: NodeStmtDoWhile) -> None:
        self.output.append("    ;do while loop\n")
        end_label = self.create_label()
        reset_label = self.create_label()
        self.loop_end_labels.append(end_label)

        self.output.append(reset_label  + ":\n")

        self.generate_scope(do_while_stmt.scope)

        self.generate_expression(do_while_stmt.expr)
        self.pop("ax")
        self.output.append("    test ax, ax\n")
        self.output.append(f"    jz {end_label}\n")

        self.output.append("    jmp " + reset_label + "\n")
        self.output.append(end_label  + ":\n")
        self.output.append("    ;/do while loop\n")
        self.loop_end_labels.pop()

    def generate_for(self, for_stmt: NodeStmtFor) -> None:
        self.output.append("    ;for loop\n")
        end_label = self.create_label()
        reset_label = self.create_label()
        self.loop_end_labels.append(end_label)

        self.generate_let(for_stmt.ident_def)

        self.output.append(reset_label  + ":\n")

        self.generate_comparison_expression(for_stmt.condition)
        
        self.pop("ax")
        self.output.append("    test ax, ax\n")
        self.output.append(f"    jz {end_label}\n")

        self.generate_scope(for_stmt.scope)
        
        self.generate_reassign(for_stmt.ident_assign)

        self.output.append("    jmp " + reset_label + "\n")
        self.output.append(end_label  + ":\n")
        self.output.append("    add rsp, " + str(8) + "\n")
        self.stack_size -= self.stack_item_sizes.pop() # does this to remove the variable after the i loop ends
        self.variables.popitem()
        self.output.append("    ;/for loop\n")
        self.loop_end_labels.pop()

    def generate_print(self, print_stmt: NodeStmtPrint) -> None:
        if isinstance(print_stmt.content, NodeExpr):
            self.generate_expression(print_stmt.content)
        elif isinstance(print_stmt.content, NodeTermChar):
            self.generate_char(print_stmt.content)
        expr_loc = f"rsp"
        self.output.append("    ; printing\n")
        self.output.append("    mov rax, 1\n")
        self.output.append("    mov rdi, 1\n")
        self.output.append(f"    mov rsi, {expr_loc}\n")
        self.output.append("    mov rdx, 1\n")
        self.output.append("    syscall\n")
        pushed_res = self.stack_item_sizes.pop() #it removes the printed expression because it causes a mess in the stack when looping
        self.output.append("    add rsp, " + str(pushed_res) + "\n") #removes the printed expression from the stack
        self.stack_size -= pushed_res #lowers the stack size
        self.output.append("    ; /printing\n")

    def generate_statement(self, statement: NodeStmt) -> None:
        """
        generates a statement based on the node given
        """
        if isinstance(statement.stmt_var, NodeStmtExit):
            self.generate_exit(statement.stmt_var)

        elif isinstance(statement.stmt_var, NodeStmtLet):
            self.generate_let(statement.stmt_var)
        
        elif isinstance(statement.stmt_var, NodeScope):
            self.generate_scope(statement.stmt_var)
        
        elif isinstance(statement.stmt_var, NodeStmtIf):
            self.generate_if_statement(statement.stmt_var)

        elif isinstance(statement.stmt_var, NodeStmtReassign):
            self.generate_reassign(statement.stmt_var)

        elif isinstance(statement.stmt_var, NodeStmtWhile):
            self.generate_while(statement.stmt_var)
        
        elif isinstance(statement.stmt_var, NodeStmtDoWhile):
            self.generate_do_while(statement.stmt_var)
        
        elif isinstance(statement.stmt_var, NodeStmtFor):
            self.generate_for(statement.stmt_var)
        
        elif isinstance(statement.stmt_var, NodeStmtPrint):
            self.generate_print(statement.stmt_var)

        elif isinstance(statement.stmt_var, NodeStmtBreak):
            if self.loop_end_labels:
                self.output.append("    ; break \n")
                self.output.append("    jmp " + self.loop_end_labels[-1] + "\n")
            else:
                self.raise_error("Syntax", "cant break out of a loop when not inside one")

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
