from hdzerrors import ErrorHandler
from comptypes import *
import hdztokentypes as tt


class Generator(ErrorHandler):
    output: list[str] = []
    stack_size: size_bytes = 0 # 8 bits (a byte) as a unit
    stack_item_sizes: list[size_bytes] = [] # same as above

    variables: list[VariableContext] = [] # stores all variables on the stack
    
    # scopes stores the amount of variables in the scope
    # defaulted with 0 so the global scope doesn't throw an exception when slicing the vars list
    scopes: list[int] = [0]
    
    label_count: int = 0
    loop_end_labels: list[str] = []

    registers_64bit: tuple[str, ...] = (
        "rax", "rbx", "rcx", "rdx",  
        "rsi", "rdi", "rsp", "rbp", 
        "r8", "r9", "r10", "r11", 
        "r12", "r13", "r14", "r15"
    )

    registers_32bit: tuple[str, ...] = (
        "eax", "ebx", "ecx", "edx",  
        "esi", "edi", "esp", "ebp", 
        "r8d", "r9d", "r10d", "r11d", 
        "r12d", "r13d", "r14d", "r15d"
    )
    
    registers_16bit: tuple[str, ...] = (
        "ax", "bx", "cx", "dx", 
        "si", "di", "sp", "bp", 
        "r8w", "r9w", "r10w", "r11w", 
        "r12w", "r13w", "r14w", "r15w"
    )

    registers_8bit: tuple[str, ...] = (
        "al", "bl", "cl", "dl", 
        "sil", "dil", "spl", "bpl", 
        "r8b", "r9b", "r10b", "r11b", 
        "r12b", "r13b", "r14b", "r15b"
    )
    
    reg_lookup_table: dict[int, tuple[str, ...]] = {
        1: registers_8bit,
        2: registers_16bit,
        4: registers_32bit,
        8: registers_64bit,
    }
    
    def __init__(self, program: NodeProgram, file_content: str) -> None:
        super().__init__(file_content)
        self.main_program: NodeProgram = program

        self.column_number = -1
        
        # self.data_section_index: int = 1
        # self.bss_section_index: int = 2
    
    def push_stack(self, loc: str, size_words: str = ""):
        """
        adds a push instruction to the output and updates the stack size 
        """
        if loc in self.registers_64bit or loc.startswith("QWORD") or size_words == "QWORD":
            size: size_bytes = 8
            reg = "rax"
        elif loc in self.registers_32bit or loc.startswith("DWORD") or size_words == "DWORD":
            size: size_bytes = 4
            reg = "eax"
        elif loc in self.registers_16bit or loc.startswith("WORD") or size_words == "WORD":
            size: size_bytes = 2
            reg = "ax"
        elif loc in self.registers_8bit or loc.startswith("BYTE") or size_words == "BYTE":
            size: size_bytes = 1
            reg = "al"
        else:
            raise ValueError("Invalid register / WORD size")
        
        if "[" not in loc:
            self.output.append(f"    mov {size_words}[rbp - {self.stack_size}], {loc} ;push\n")
        else:
            self.output.append(f"    mov {reg}, {loc}\n")
            self.output.append(f"    mov {size_words}[rbp - {self.stack_size}], {reg} ;push\n")
        self.stack_size += size
        self.stack_item_sizes.append(size)
        if ErrorHandler.debug_mode:
            print("push", self.stack_size, self.stack_item_sizes, self.variables)

    def pop_stack(self, reg: str):
        """
        adds a pop instruction to the output and updates the stack size 
        """
        self.stack_size -= self.stack_item_sizes.pop() # removes and gives the last items size
        self.output.append(f"    mov {reg}, [rbp - {self.stack_size}] ;pop\n")
        if ErrorHandler.debug_mode:
            print("pop", self.stack_size, self.stack_item_sizes, self.variables)
    
    def get_reg(self, idx: int) -> str:
        """
        returns a name of the correctly sized register based on the current top of the stack
        """
        assert len(self.stack_item_sizes) > 0, "Stack underflow"
        size = self.stack_item_sizes[-1]
        return self.reg_lookup_table[size][idx]

    def create_label(self, custom_lbl: str="") -> str:
        """
        returns a name for a new label based on the amount of labels already created
        """
        self.label_count += 1
        return f".lbl{custom_lbl}{self.label_count}"

    def begin_scope(self) -> None:
        """
        only used in the gen_scope() method,
        adds the amount of variables to the scopes list 
        so the end scopes function knows how many variables it should delete
        """
        self.scopes.append(len(self.variables))

    def end_scope(self) -> None:
        """
        only used in the gen_scope() method,
        removes the last scopes variables from memory (by moving the stack pointer),
        removes itself from the generators list of scopes,
        removes the aforementioned variables from the generators dictionary
        returns prematurely if theres nothing to remove
        """
        pop_count: int = len(self.variables) - self.scopes[-1]
        if pop_count == 0:
            return # nothing to remove, if its not here then slice accepts all of the stack -> list[0:] == list

        popped_size: int = sum(self.stack_item_sizes[-pop_count:])
        self.stack_size -= popped_size

        for _ in range(pop_count):
            self.variables.pop()
            self.stack_item_sizes.pop()
        del self.scopes[-1]

    def gen_term(self, term: NodeTerm) -> None:
        """
        generates a term, a term being a variable or a number, 
        gets pushed on to of the stack
        """
        if ErrorHandler.debug_mode:
            print(term.var)
        
        if isinstance(term.var, NodeTermInt):
            assert term.var.int_lit.value is not None, "term.var.int_lit.value shouldn't be None, probably a parsing error"
            
            if term.negative:
                term.var.int_lit.value = "-" + term.var.int_lit.value
            self.push_stack(term.var.int_lit.value, "DWORD")
        elif isinstance(term.var, NodeTermIdent):
            assert term.var.ident.value is not None, "term.var.ident.value shouldn't be None, probably a parsing error"

            found_vars: tuple[VariableContext, ...] = tuple(filter(lambda x: x.name == term.var.ident.value, self.variables)) # type: ignore (says types are unknown even though they are known)
            if not found_vars:
                self.raise_error("Value", f"variable was not declared: {term.var.ident.value}", term.var.ident)
            
            location, word_size = found_vars[-1].loc, found_vars[-1].size_w

            self.push_stack(f"{word_size} [rbp - {location}]") # QWORD 64 bits (word = 16 bits)
            
            if term.negative:
                self.output.append(f"    neg {word_size}[rbp - {self.stack_size - self.stack_item_sizes[-1]}]\n")
        elif isinstance(term.var, NodeTermBool):
            assert term.var.bool.value is not None, "shouldn't be None here"
            self.push_stack(term.var.bool.value, "BYTE")
        elif isinstance(term.var, NodeTermParen):
            self.gen_expression(term.var.expr)
            if term.negative:
                ra = self.get_reg(0)
                self.pop_stack(ra)
                self.output.append(f"    neg {ra}\n")
                self.push_stack(ra)
        elif isinstance(term.var, NodeTermNot):
            self.gen_term(term.var.term) # type: ignore (type checking freaking out)
            ra = self.get_reg(0)
            rb = self.get_reg(1)
            self.pop_stack(rb)
            self.output.append(f"    xor {ra}, {ra}\n")
            self.output.append(f"    test {rb}, {rb}\n")
            self.output.append("    sete al\n")
            self.push_stack(ra)
    
    def gen_predicate_expression(self, comparison: NodePredExpr) -> None:
        """
        generates a comparison expression that pushes a 16bit value onto the stack,
        type of binary expression that returns 1 or 0 depending on if its true or false
        """
        self.gen_expression(comparison.rhs)
        self.gen_expression(comparison.lhs)
        ra = self.get_reg(0)
        rb = self.get_reg(1)
        self.pop_stack(ra)
        self.pop_stack(rb)
        self.output.append(f"    cmp {ra}, {rb}\n")
        if comparison.comp_sign.type == tt.IS_EQUAL:
            self.output.append("    sete al\n")
        elif comparison.comp_sign.type == tt.IS_NOT_EQUAL:
            self.output.append("    setne al\n")
        elif comparison.comp_sign.type == tt.LARGER_THAN:
            self.output.append("    setg al\n")
        elif comparison.comp_sign.type == tt.LESS_THAN:
            self.output.append("    setl al\n")
        elif comparison.comp_sign.type == tt.LARGER_THAN_OR_EQ:
            self.output.append("    setge al\n")
        elif comparison.comp_sign.type == tt.LESS_THAN_OR_EQ:
            self.output.append("    setle al\n")
        else:
            self.raise_error("Syntax", "Invalid comparison expression", comparison.comp_sign)
        self.push_stack("al")

    def gen_logical_expression(self, logic_expr: NodeExprLogic) -> None:
        """
        generates an eval for a logical expression (AND or OR) that pushes a 16bit value onto the stack,
        its result can be either 1 or 0
        """
        self.gen_expression(logic_expr.rhs)
        self.gen_expression(logic_expr.lhs)
        ra = self.get_reg(0)
        rb = self.get_reg(1)
        rc = "cl"
        self.pop_stack(ra)
        self.pop_stack(rb)
        self.output.append(f"    mov {rc}, {ra}\n")
        self.output.append(f"    test {rb}, {rb}\n")

        label = self.create_label()
        if logic_expr.logical_operator.type == tt.AND:
            self.output.append(f"    jnz {label}\n")
            self.output.append(f"    mov {rc}, {rb}\n")
        elif logic_expr.logical_operator.type == tt.OR:
            self.output.append(f"    jz {label}\n")
            self.output.append(f"    mov {rc}, {rb}\n")
        else:
            self.raise_error("Syntax", "Invalid logic expression", logic_expr.logical_operator)
        self.output.append(f"{label}:\n")
        self.output.append(f"    test {ra}, {ra}\n")
        self.output.append("    setne al\n")
        self.push_stack("al")

    def gen_binary_expression(self, bin_expr: NodeBinExpr) -> None:
        """
        generates a binary expression that gets pushed on top of the stack
        """
        ra = self.get_reg(0) #! note could cause problems with overwriting results
        rb = self.get_reg(1)

        if isinstance(bin_expr.var, NodeBinExprAdd):
            self.gen_expression(bin_expr.var.rhs)
            self.gen_expression(bin_expr.var.lhs)
            self.pop_stack(ra)
            self.pop_stack(rb)
            self.output.append(f"    add {ra}, {rb}\n")
            self.push_stack(ra)
        elif isinstance(bin_expr.var, NodeBinExprMulti):
            self.gen_expression(bin_expr.var.rhs)
            self.gen_expression(bin_expr.var.lhs)
            self.pop_stack(ra)
            self.pop_stack(rb)
            self.output.append(f"    mul {rb}\n")
            self.push_stack(ra)
        elif isinstance(bin_expr.var, NodeBinExprSub):
            self.gen_expression(bin_expr.var.rhs)
            self.gen_expression(bin_expr.var.lhs)
            self.pop_stack(ra)
            self.pop_stack(rb)
            self.output.append(f"    sub {ra}, {rb}\n")
            self.push_stack(ra)
        elif isinstance(bin_expr.var, NodeBinExprDiv):
            self.gen_expression(bin_expr.var.rhs)
            self.gen_expression(bin_expr.var.lhs)
            self.pop_stack(ra)
            self.pop_stack(rb)
            self.output.append(f"    idiv {rb}\n") #! NOTE: idiv is used because div only works with unsigned numbers
            self.push_stack(ra)
        elif isinstance(bin_expr.var, NodeBinExprMod):
            self.gen_expression(bin_expr.var.rhs)
            self.gen_expression(bin_expr.var.lhs)
            self.pop_stack(ra)
            self.pop_stack(rb)
            self.output.append("    xor rdx, rdx\n")
            self.output.append("    cqo\n") # sign extends so the modulus result can be negative
            self.output.append(f"    idiv {rb}\n")
            #TODO: make division be generic for any size
            self.push_stack("edx") # assembly stores the modulus in rdx after the standard division instruction
        else:
            self.raise_error("Generator", "failed to generate binary expression")

    def gen_bool_expression(self, expression: NodeExprBool):
        if isinstance(expression.var, NodePredExpr):
            self.gen_predicate_expression(expression.var)
        elif isinstance(expression.var, NodeExprLogic):
            self.gen_logical_expression(expression.var)

    def gen_expression(self, expression: NodeExpr) -> None:
        """
        generates an expression and pushes it on top of the stack
        """
        if isinstance(expression.var, NodeTerm):
            self.gen_term(expression.var)
        elif isinstance(expression.var, NodeBinExpr):
            self.gen_binary_expression(expression.var)
        elif isinstance(expression.var, NodeExprBool):
            self.gen_bool_expression(expression.var)
    
    def gen_char(self, char: NodeTermChar) -> None:
        assert char.char.value is not None, "char should have value here"
        self.push_stack(char.char.value, "BYTE")

    def gen_scope(self, scope: NodeScope) -> None:
        self.begin_scope()
        for stmt in scope.stmts:
            self.gen_statement(stmt)
        self.end_scope()

    def gen_if_predicate(self, pred: NodeIfPred, end_label: str) -> None:
        """
        generates the following statements connected to the if statement if there are any
        """
        if isinstance(pred.var, NodeIfPredElif):
            self.output.append("    ;; --- elif ---\n")
            self.gen_expression(pred.var.expr)
            label = self.create_label()

            first_reg = self.get_reg(0)
            self.pop_stack(first_reg)
            self.output.append(f"    test {first_reg}, {first_reg}\n")
            
            self.output.append(f"    jz {label}\n")
            self.gen_scope(pred.var.scope)
            self.output.append(f"    jmp {end_label}\n")
            self.output.append(f"{label}:\n")
            if pred.var.pred is not None:
                self.gen_if_predicate(pred.var.pred, end_label)
        elif isinstance(pred.var, NodeIfPredElse): # type: ignore (here just so the else can catch mistakes)
            self.output.append("    ;; --- else ---\n")
            self.gen_scope(pred.var.scope)
        else:
            raise ValueError("Unreachable")

    def gen_let(self, let_stmt: NodeStmtLet):
        found_vars: tuple[VariableContext, ...] = tuple(filter(lambda x: x.name == let_stmt.ident.value, self.variables[self.scopes[-1]::]))
        if found_vars:
            self.raise_error("Value", f"variable has been already declared in this scope: {let_stmt.ident.value}", curr_token=let_stmt.ident)
        location: int = self.stack_size # stack size changes after generating the expression, thats why its saved here

        if let_stmt.type_.type == tt.INT_DEF:
            self.output.append("    ;; --- int var declaration ---\n")
            word_size: size_words = "DWORD"
            byte_size: size_bytes = 4
            #TODO: maybe handle incorrect types in the parser instead
            if isinstance(let_stmt.expr.var, NodeExprBool):
                self.raise_error("Type", "cannot assign a boolean expression to `int`")
            elif isinstance(let_stmt.expr.var, NodeTerm) and isinstance(let_stmt.expr.var.var, NodeTermBool):
                self.raise_error("Type", "cannot assign `bool` to `int`", let_stmt.expr.var.var.bool)
            self.gen_expression(let_stmt.expr)
        elif let_stmt.type_.type == tt.BOOL_DEF:
            self.output.append("    ;; --- bul var declaration ---\n")
            word_size: size_words = "BYTE"
            byte_size: size_bytes = 1
            if isinstance(let_stmt.expr.var, NodeBinExpr):
                self.raise_error("Type", "cannot assign `int` to `bool`")
            elif let_stmt.expr.var is not None and isinstance(let_stmt.expr.var.var, NodeTermInt):
                self.raise_error("Type", "cannot assign `int` to `bool`") # add guarding for other int expression (parenthesis and stuff)

            self.gen_expression(let_stmt.expr)
        else:
            raise ValueError("Unreachable")
        
        assert let_stmt.ident.value is not None, "var name shouldn't be None here"
        self.variables.append(VariableContext(let_stmt.ident.value, location, word_size, byte_size))

    def gen_reassign(self, reassign_stmt: NodeStmtReassign):
        assert reassign_stmt.var.ident.value is not None, "has to be a string, probably a mistake in parsing"
        
        found_vars: tuple[VariableContext, ...] = tuple(filter(lambda x: x.name == reassign_stmt.var.ident.value, self.variables))
        
        if not found_vars:
            self.raise_error("Value", f"undeclared identifier: {reassign_stmt.var.ident.value}", reassign_stmt.var.ident)
        
        if isinstance(reassign_stmt.var, NodeStmtReassignEq):
            self.output.append("    ;; --- var reassign ---\n")
            self.gen_expression(reassign_stmt.var.expr)
            ra = self.get_reg(0)
            self.pop_stack(ra)
            var_ctx = found_vars[-1]
            location = var_ctx.loc
            self.output.append(f"    mov [rbp - {location}], {ra}\n")
        elif isinstance(reassign_stmt.var, (NodeStmtReassignInc, NodeStmtReassignDec)): # type: ignore (using an else branch to catch errors)
            self.output.append("    ;; --- var inc / dec ---\n")
            var_ctx = found_vars[-1]
            location, size_words = var_ctx.loc, var_ctx.size_w
            self.push_stack(f"{size_words} [rbp - {location}]") # QWORD 64 bits (word = 16 bits)
            ra = self.get_reg(0)
            self.pop_stack(ra)
            self.output.append(f"    inc {ra}\n" 
                                if isinstance(reassign_stmt.var, NodeStmtReassignInc) 
                                else f"    dec {ra}\n")
            self.output.append(f"    mov [rbp - {location}], {ra}\n")
        else:
            raise ValueError("Unreachable")

    def gen_exit(self, exit_stmt: NodeStmtExit) -> None:
        self.gen_expression(exit_stmt.expr)
        self.output.append("    ;; --- exit ---\n")
        self.output.append("    mov rax, 60\n")
        rdi = self.get_reg(5) # rdi / di is 5th register
        self.pop_stack(rdi)
        self.output.append("    syscall\n")

    def gen_if_statement(self, if_stmt: NodeStmtIf) -> None:
        self.output.append("    ;; --- if block ---\n")
        self.gen_expression(if_stmt.expr)
        label = self.create_label()
        
        first_reg = self.get_reg(0)
        self.pop_stack(first_reg)
        self.output.append(f"    test {first_reg}, {first_reg}\n")

        self.output.append(f"    jz {label}\n")
        self.gen_scope(if_stmt.scope)
        
        if if_stmt.ifpred is not None:
            end_label = self.create_label()
            self.output.append(f"    jmp {end_label}\n")
            self.output.append(f"{label}:\n")
            self.gen_if_predicate(if_stmt.ifpred, end_label)
            self.output.append(f"{end_label}:\n")
        else:
            self.output.append(f"{label}:\n")

    def gen_while(self, while_stmt: NodeStmtWhile) -> None:
        self.output.append("    ;; --- while loop ---\n")
        end_label = self.create_label()
        reset_label = self.create_label()
        self.loop_end_labels.append(end_label)

        self.output.append(f"{reset_label}:\n")

        self.gen_expression(while_stmt.expr)
        first_reg = self.get_reg(0)
        self.pop_stack(first_reg)
        self.output.append(f"    test {first_reg}, {first_reg}\n")
        self.output.append(f"    jz {end_label}\n")

        self.gen_scope(while_stmt.scope)
        
        self.output.append(f"    jmp {reset_label}\n")
        self.output.append(f"{end_label}:\n")
        self.loop_end_labels.pop()

    def gen_do_while(self, do_while_stmt: NodeStmtDoWhile) -> None:
        self.output.append("    ;; --- do while loop ---\n")
        end_label = self.create_label()
        reset_label = self.create_label()
        self.loop_end_labels.append(end_label)

        self.output.append(f"{reset_label}:\n")

        self.gen_scope(do_while_stmt.scope)

        self.gen_expression(do_while_stmt.expr)
        
        first_reg = self.get_reg(0)
        self.pop_stack(first_reg)
        self.output.append(f"    test {first_reg}, {first_reg}\n")
        self.output.append(f"    jz {end_label}\n")

        self.output.append(f"    jmp {reset_label}\n")
        self.output.append(f"{end_label}:\n")
        self.loop_end_labels.pop()

    def gen_for(self, for_stmt: NodeStmtFor) -> None:
        self.output.append("    ;; --- for loop ---\n")
        end_label = self.create_label("end")
        reset_label = self.create_label("rst")
        self.loop_end_labels.append(end_label)

        self.gen_let(for_stmt.ident_def)

        self.output.append(f"{reset_label}:\n")

        self.gen_predicate_expression(for_stmt.condition)

        first_reg = self.get_reg(0)
        self.pop_stack(first_reg)
        self.output.append(f"    test {first_reg}, {first_reg}\n")
        self.output.append(f"    jz {end_label}\n")

        self.gen_scope(for_stmt.scope)
        
        self.gen_reassign(for_stmt.ident_assign)

        self.output.append(f"    jmp {reset_label}\n")
        self.output.append(f"{end_label}:\n")
        self.stack_size -= self.stack_item_sizes.pop() # does this to remove the variable after the i loop ends
        self.variables.pop()
        self.loop_end_labels.pop()

    def gen_print(self, print_stmt: NodeStmtPrint) -> None:
        self.output.append("    ;; --- print char ---\n")
        if isinstance(print_stmt.content, NodeExpr):
            self.gen_expression(print_stmt.content)
        elif isinstance(print_stmt.content, NodeTermChar): # type: ignore (using an else branch to catch errors)
            self.gen_char(print_stmt.content)
        else:
            raise ValueError("unreachable")
        
        expr_loc = f"[rbp - {self.stack_size - self.stack_item_sizes[-1]}]"
        self.output.append("    mov rax, 1\n")
        self.output.append("    mov rdi, 1\n")
        self.output.append(f"    lea rsi, {expr_loc}\n")
        self.output.append("    mov rdx, 1\n")
        self.output.append("    syscall\n")
        pushed_res = self.stack_item_sizes.pop() #it removes the printed expression because it causes a mess in the stack when looping
        self.stack_size -= pushed_res #lowers the stack size

    def gen_statement(self, statement: NodeStmt) -> None:
        """
        generates a statement based on the node passed in
        """
        if isinstance(statement.stmt_var, NodeStmtExit):
            self.gen_exit(statement.stmt_var)
        elif isinstance(statement.stmt_var, NodeStmtLet):
            self.gen_let(statement.stmt_var)
        elif isinstance(statement.stmt_var, NodeScope):
            self.gen_scope(statement.stmt_var)
        elif isinstance(statement.stmt_var, NodeStmtIf):
            self.gen_if_statement(statement.stmt_var)
        elif isinstance(statement.stmt_var, NodeStmtReassign):
            self.gen_reassign(statement.stmt_var)
        elif isinstance(statement.stmt_var, NodeStmtWhile):
            self.gen_while(statement.stmt_var)
        elif isinstance(statement.stmt_var, NodeStmtDoWhile):
            self.gen_do_while(statement.stmt_var)
        elif isinstance(statement.stmt_var, NodeStmtFor):
            self.gen_for(statement.stmt_var)
        elif isinstance(statement.stmt_var, NodeStmtPrint):
            self.gen_print(statement.stmt_var)
        elif isinstance(statement.stmt_var, NodeStmtBreak):
            if self.loop_end_labels:
                self.output.append("    ;; --- break --- \n")
                self.output.append(f"    jmp {self.loop_end_labels[-1]}\n")
            else:
                self.raise_error("Syntax", "cant break out of a loop when not inside one")

    def gen_program(self) -> list[str]:
        """
        generates the whole assembly based on the nodes that are given,
        returns a list of strings that contains the assembly instructions
        """
        self.output.append("section .text\n    global _start\n")
        self.output.append("_start:\n    mov rbp, rsp\n")

        for stmt in self.main_program.stmts:
            assert stmt is not None, "None statement shouldn't make it here"
            self.gen_statement(stmt)

        self.output.append("    ;; --- default exit ---\n    mov rax, 60\n    mov rdi, 0\n    syscall\n" )
        self.output.append("section .data\n")
        self.output.append("section .bss\n")
        return self.output
