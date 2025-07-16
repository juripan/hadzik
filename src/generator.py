from collections.abc import Callable
import itertools
from errors import ErrorHandler
from comptypes import *
import tokentypes as tt


class Generator(ErrorHandler):
    output: list[str] = []
    section_data: list[str] = []

    stack_size: size_bytes = 0
    stack_item_sizes: list[list[size_bytes]] = []
    stack_padding: list[list[size_bytes]] = []

    variables: list[VariableContext] = [] # stores all variables on the stack
    functions: list[str] = []
    
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

    get_type_size: dict[token_type, int] = {
        BOOL_DEF: 1,
        CHAR_DEF: 1,
        INT_DEF: 4,
        STR_DEF: 8
    }
    
    def __init__(self, program: NodeProgram, file_content: str) -> None:
        super().__init__(file_content)
        self.main_program: NodeProgram = program

        self.column_number = -1

        # What if every Node had its generation as its own method and not a method of the generator?
        # Hmmmmmmmmm
        self.map_generate_func: dict[object, Callable] = {
            NodeStmtExit: self.gen_exit,
            NodeStmtDeclare: self.gen_decl,
            NodeScope: self.gen_scope,
            NodeStmtIf: self.gen_if_statement,
            NodeStmtReassign: self.gen_reassign,
            NodeStmtWhile: self.gen_while,
            NodeStmtDoWhile: self.gen_do_while,
            NodeStmtFor: self.gen_for,
            NodeStmtPrint: self.gen_print,
            NodeStmtBreak: self.gen_break,
        }

    def align_stack(self, size: size_bytes) -> size_bytes:
        padding = 0
        if self.stack_size % 2 != 0 and size > 1:
            padding = 2 - self.stack_size % 2
            self.stack_size += 2 - self.stack_size % 2
        return padding
    
    def call_func(self, name: str) -> None:
        """
        adds a call instruction corresponding to the given function name
        """
        self.output.append(f"    lea rsp, [rbp - {self.stack_size}]\n")
        self.output.append(f"    call {name}\n")

        if name not in self.functions:
            self.functions.append(name)
    
    def add_funcs(self) -> None:
        """
        adds all of the function bodies that were used into the assembly
        """
        for func in self.functions:
            self.output.append(f"{func}:\n")
            if func == "exit":
                self.output.append(
                    "    mov rax, 60\n"
                    "    syscall\n"
                )
            elif func == "print_char":
                self.output.append(
                    "    mov rax, 1\n"
                    "    mov rdi, 1\n"
                    "    mov rdx, 1\n"
                    "    syscall\n"
                    "    ret\n"
                )
            elif func == "print_str":
                self.output.append(
                    "    mov rax, 1\n"
                    "    mov rdi, 1\n"
                    "    syscall\n"
                    "    ret\n"
                    )
            else:
                raise ValueError("Unreachable")

    def push_stack(self, src: str, size_words: str = "") -> None:
        """
        adds a 'push' instruction to the output and updates the stack size 
        """
        if src in self.registers_64bit or src.startswith("QWORD") or size_words == "QWORD":
            size: size_bytes = 8
            reg = "rax"
        elif src in self.registers_32bit or src.startswith("DWORD") or size_words == "DWORD":
            size: size_bytes = 4
            reg = "eax"
        elif src in self.registers_16bit or src.startswith("WORD") or size_words == "WORD":
            size: size_bytes = 2
            reg = "ax"
        elif src in self.registers_8bit or src.startswith("BYTE") or size_words == "BYTE":
            size: size_bytes = 1
            reg = "al"
        else:
            raise ValueError(f"Invalid register / WORD size {src}")
        
        padding = self.align_stack(size)

        self.stack_size += size
        self.stack_item_sizes.append([size])
        self.stack_padding.append([padding])


        if "[" not in src:
            self.output.append(f"    mov {size_words} [rbp - {self.stack_size}], {src} ;push\n")
        else:
            self.output.append(
                f"    mov {reg}, {src}\n"
                f"    mov {size_words} [rbp - {self.stack_size}], {reg} ;push\n"
            )
        
        if ErrorHandler.debug_mode:
            print("push", self.stack_size, self.stack_item_sizes, self.stack_padding, self.variables)

    def pop_stack(self, dest_reg: str):
        """
        adds a 'pop' instruction to the output and updates the stack size 
        """
        self.output.append(f"    mov {dest_reg}, [rbp - {self.stack_size}] ;pop\n")
        size = self.stack_item_sizes.pop() # removes the last items size
        padding = self.stack_padding.pop()
        
        self.stack_size -= sum(size + padding)
        
        if ErrorHandler.debug_mode:
            print("pop", self.stack_size, self.stack_item_sizes, self.stack_padding, self.variables)
    
    def push_stack_complex(self, src: list[str], sizes_w: list[size_words], sizes_b: list[size_bytes]):
        """
        pushes multiple items onto the stack but only saves it as a whole item onto the compiler stack
        """
        #TODO: figure out what to do with the padding here
        padding = 0
        for item, byte_s, word_s in zip(src, sizes_b, sizes_w):
            # padding += self.align_stack(byte_s)
            self.stack_size += byte_s
            if word_s == "QWORD" and item not in self.registers_64bit:
                self.output.append(f"    mov rbx, {item}\n"
                    f"    mov {word_s} [rbp - {self.stack_size}], rbx ;push\n"
                )
            else:
                self.output.append(f"    mov {word_s} [rbp - {self.stack_size}], {item} ;push\n")
        
        self.stack_item_sizes.append([sum(sizes_b)])
        self.stack_padding.append([padding])
        if ErrorHandler.debug_mode:
            print("push multi", self.stack_size, self.stack_item_sizes, self.variables)

    def get_reg(self, idx: int) -> str:
        """
        returns a name of the correctly sized register based on the current top of the stack
        if the size doesn't exist throws a ValueError
        """
        assert len(self.stack_item_sizes) > 0, "Stack underflow"
        size = self.stack_item_sizes[-1]
        if len(size) != 1:
            raise ValueError(self.stack_item_sizes)
        return self.reg_lookup_table[size[0]][idx]

    def create_label(self, custom_lbl: str="") -> str:
        """
        returns a name for a new label based on the amount of labels already created
        """
        self.label_count += 1
        return f".lbl{custom_lbl}{self.label_count}"

    def begin_scope(self) -> None:
        """
        adds the amount of variables to the scopes list 
        so the end scopes function knows how many variables it should delete,
        only used in the gen_scope() method
        """
        self.scopes.append(len(self.variables))

    def end_scope(self) -> None:
        """
        removes the last scopes variables from memory (by moving the stack pointer),
        removes itself from the generators list of scopes,
        removes the aforementioned variables from the generators dictionary
        returns prematurely if theres nothing to remove,
        only used in the gen_scope() method
        """
        pop_count: int = len(self.variables) - self.scopes[-1]
        if pop_count == 0:
            del self.scopes[-1]
            return # nothing to remove, if its not here then slice accepts all of the stack -> list[0:] == list
        popped_size: int = sum(itertools.chain.from_iterable(self.stack_item_sizes[-pop_count:] + self.stack_padding[-pop_count:]))
        self.stack_size -= popped_size

        for _ in range(pop_count):
            self.variables.pop()
            self.stack_item_sizes.pop()
            self.stack_padding.pop()
        del self.scopes[-1]
    
    def make_str(self, str_term: NodeTermStr):
        """
        adds a string onto the stack with its pointer to the start and length
        """
        if not str_term.string.value:
            str_term.string.value = "0"
        
        str_data = list(map(lambda x: hex(int(x))[2:], str_term.string.value.split(",")[::-1]))
        STR_LEN = len(str_data)
        
        str_chunks: list[str] = []
        str_data_sizeb: list[size_bytes] = []
        str_data_sizew: list[size_words] = []
        
        start = 0
        end = 0
        count = STR_LEN

        for sizeb, sizew in zip((8, 4, 2, 1), ("QWORD", "DWORD", "WORD", "BYTE")):
            res = count // sizeb
            count %= sizeb

            for i in range(res):
                end += sizeb
                str_chunks.append("0x" + "".join(str_data[start:end]))
                str_data_sizeb.append(sizeb)
                str_data_sizew.append(sizew)
                start += sizeb
        
        self.output.append(f"    lea rax, [rbp - {self.stack_size + STR_LEN}]\n")
        str_chunks.append("rax")
        str_data_sizeb.append(8)
        str_data_sizew.append("QWORD")
        
        if str_term.string.value != "0":
            str_chunks.append(str(STR_LEN))
        else:
            str_chunks.append("0")
        
        str_data_sizeb.append(4)
        str_data_sizew.append("DWORD")
        
        self.push_stack_complex(str_chunks, str_data_sizew, str_data_sizeb)


    def gen_term(self, term: NodeTerm) -> None:
        """
        generates a term, a term being a variable or a number, 
        gets pushed on to of the stack
        """
        if ErrorHandler.debug_mode:
            print(term.var)
        
        if term.index is not None:
            self.output.append("    ; --- indexing ---\n")
            old_stack_size = self.stack_size # solves the incorrect reads
            LEN_SIZE = 4
            ITEM_SIZE_W = "BYTE"
            ITEM_SIZE_B = 1
            
            self.gen_expression(term.index)

            rb = self.get_reg(1)
            self.output.append(f"    xor rbx, rbx\n")
            self.pop_stack(rb)

            self.gen_term(NodeTerm(term.var))
            self.output.append(f"    mov rax, [rbp - {self.stack_size - LEN_SIZE}]\n") # reads the pointer to the string
            
            self.stack_size = old_stack_size
            self.stack_item_sizes.pop()

            self.push_stack(f"{ITEM_SIZE_W} [rax + rbx * {ITEM_SIZE_B}]")
        elif isinstance(term.var, NodeTermInt):
            assert term.var.int_lit.value is not None, "term.var.int_lit.value shouldn't be None, probably a parsing error"
            
            if term.var.negative:
                term.var.int_lit.value = "-" + term.var.int_lit.value
            self.push_stack(term.var.int_lit.value, "DWORD")
        elif isinstance(term.var, NodeTermIdent):
            assert term.var.ident.value is not None, "term.var.ident.value shouldn't be None, probably a parsing error"

            found_vars: tuple[VariableContext, ...] = tuple(filter(lambda x: x.name == term.var.ident.value, self.variables)) # type: ignore (says types are unknown even though they are known)
            if not found_vars:
                self.compiler_error("Value", f"variable was not declared: {term.var.ident.value}", term.var.ident)
            if found_vars[-1].size_w == "STR": # reading a str type
                len_loc = found_vars[-1].loc
                LEN_SIZE = "DWORD"
                PTR_SIZE = "QWORD"

                self.push_stack(f"{PTR_SIZE} [rbp - {len_loc - 4}]")
                self.push_stack(f"{LEN_SIZE} [rbp - {len_loc}]")
                accum_size = self.stack_item_sizes.pop() + self.stack_item_sizes.pop()
                accum_padding = self.stack_padding.pop() + self.stack_padding.pop()
                self.stack_item_sizes.append(accum_size)
                self.stack_padding.append(accum_padding)
            else:
                location, word_size = found_vars[-1].loc, found_vars[-1].size_w
                self.push_stack(f"{word_size} [rbp - {location}]")

                if term.var.negative:
                    assert len(self.stack_item_sizes[-1]) == 1, "cannot negate a non primitive type (str or array)"
                    self.output.append(f"    neg {word_size}[rbp - {self.stack_size - self.stack_item_sizes[-1][-1]}]\n")
        elif isinstance(term.var, NodeTermBool):
            assert term.var.bool.value is not None, "shouldn't be None here"
            self.push_stack(term.var.bool.value, "BYTE")
        elif isinstance(term.var, NodeTermChar):
            assert term.var.char.value is not None, "shouldn't be None here"
            self.push_stack(term.var.char.value, "BYTE")
        elif isinstance(term.var, NodeTermStr):
            assert term.var.string.value is not None, "shouldn't be None here"
            self.make_str(term.var)
        elif isinstance(term.var, NodeTermArray):
            raise NotImplementedError("TODO: reimplement this")
            size = 0
            padding = 0
            for expr in term.var.exprs:
                self.gen_expression(expr)
                size += self.stack_item_sizes.pop()
                self.stack_padding.pop()
            
            self.output.append(f"    lea rax, [rbp - {self.stack_size}]\n")
            self.push_stack("rax")

            padding += self.stack_padding.pop()
            size += self.stack_item_sizes.pop()

            self.push_stack(str(len(term.var.exprs)), "DWORD")

            padding += self.stack_padding.pop()
            size += self.stack_item_sizes.pop()

            self.stack_item_sizes.append(size)
            self.stack_padding.append(padding)

        elif isinstance(term.var, NodeTermParen):
            self.gen_expression(term.var.expr)
            if term.var.negative:
                ra = self.get_reg(0)
                self.pop_stack(ra)
                self.output.append(f"    neg {ra}\n")
                self.push_stack(ra)
        elif isinstance(term.var, NodeTermNot):
            self.gen_term(term.var.term) # type: ignore (type checking freaking out)
            ra = self.get_reg(0)
            rb = self.get_reg(1)
            self.pop_stack(rb)
            self.output.append(
                f"    xor {ra}, {ra}\n"
                f"    test {rb}, {rb}\n"
                "    sete al\n"
            )
            self.push_stack(ra)
        elif isinstance(term.var, NodeTermBNot):
            self.gen_term(term.var.term) # type: ignore (type checking freaking out)
            ra = self.get_reg(0)
            self.pop_stack(ra)
            self.output.append(f"    not {ra}\n")
            self.push_stack(ra)
        elif isinstance(term.var, NodeTermCast):
            self.output.append("    ;--- typecast ---\n")
            self.gen_expression(term.var.expr)
            if self.stack_item_sizes[-1] not in ([1], [2], [4], [8]):
                if term.var.type.type == tt.BOOL_DEF:
                    ra = "eax"
                else:
                    raise NotImplementedError(f"{term.var.type.type} casting has not been implemented yet")
            else:
                ra = self.get_reg(0)
            
            ra_sized = self.reg_lookup_table[
                self.get_type_size[term.var.type.type]
            ][0]
            
            self.output.append(f"    xor {ra_sized}, {ra_sized}\n")
            self.pop_stack(ra)
            self.push_stack(ra_sized)
        else:
            raise ValueError("Unreachable")

    def gen_binary_expression(self, bin_expr: NodeBinExpr) -> None:
        """
        generates a binary expression that gets pushed on top of the stack
        """
        assert bin_expr is not None, "Should never trigger since its checked before calling"
        
        self.gen_expression(bin_expr.rhs)
        self.gen_expression(bin_expr.lhs)
        ra = self.get_reg(0) #NOTE: could cause problems with overwriting results
        rb = self.get_reg(1)
        rc_eq_rb = self.get_reg(2)
        self.pop_stack(ra)
        self.pop_stack(rb)

        if bin_expr.op.type == tt.PLUS:
            self.output.append(f"    add {ra}, {rb}\n")
            self.push_stack(ra)
        elif bin_expr.op.type == tt.STAR:
            self.output.append(f"    mul {rb}\n")
            self.push_stack(ra)
        elif bin_expr.op.type == tt.MINUS:
            self.output.append(f"    sub {ra}, {rb}\n")
            self.push_stack(ra)
        elif bin_expr.op.type == tt.SLASH:
            self.output.append(f"    idiv {rb}\n") #! NOTE: idiv is used because div only works with unsigned numbers
            self.push_stack(ra)
        elif bin_expr.op.type == tt.PERCENT:
            self.output.append(
                "    xor rdx, rdx\n"
                "    cqo\n" # sign extends so the modulus result can be negative
                f"    idiv {rb}\n"
            )
            #TODO: make division be generic for any size
            self.push_stack("edx") # assembly stores the modulus in rdx after the standard division instruction
        elif bin_expr.op.type == tt.BOR:
            self.output.append(f"    or {ra}, {rb}\n")
            self.push_stack(ra)
        elif bin_expr.op.type == tt.BAND:
            self.output.append(f"    and {ra}, {rb}\n")
            self.push_stack(ra)
        elif bin_expr.op.type == tt.XOR:
            self.output.append(f"    xor {ra}, {rb}\n")
            self.push_stack(ra)
        elif bin_expr.op.type == tt.SHIFT_LEFT:
            #NOTE: using arithmetic shifts because theres only signed numbers for now
            self.output.append(f"    mov {rc_eq_rb}, {rb}\n")
            self.output.append(f"    sal {ra}, cl\n")
            self.push_stack(ra)
        elif bin_expr.op.type == tt.SHIFT_RIGHT:
            self.output.append(f"    mov {rc_eq_rb}, {rb}\n")
            self.output.append(f"    sar {ra}, cl\n")
            self.push_stack(ra)
        elif bin_expr.op.type in COMPARISONS:
            self.output.append(f"    cmp {ra}, {rb}\n")
            if bin_expr.op.type == tt.IS_EQUAL:
                self.output.append("    sete al\n")
            elif bin_expr.op.type == tt.IS_NOT_EQUAL:
                self.output.append("    setne al\n")
            elif bin_expr.op.type == tt.LARGER_THAN:
                self.output.append("    setg al\n")
            elif bin_expr.op.type == tt.LESS_THAN:
                self.output.append("    setl al\n")
            elif bin_expr.op.type == tt.LARGER_THAN_OR_EQ:
                self.output.append("    setge al\n")
            elif bin_expr.op.type == tt.LESS_THAN_OR_EQ:
                self.output.append("    setle al\n")
            else:
                raise TypeError(f"Unreachable {bin_expr.op.type}")
            self.push_stack("al")
        elif bin_expr.op.type in (OR, AND):
            rc = "cl"
            self.output.append(
                f"    mov {rc}, {ra}\n"
                f"    test {rb}, {rb}\n"
            )

            label = self.create_label()
            if bin_expr.op.type == tt.AND:
                self.output.append(
                    f"    jnz {label}\n"
                    f"    mov {rc}, {rb}\n"
                )
            elif bin_expr.op.type == tt.OR:
                self.output.append(
                    f"    jz {label}\n"
                    f"    mov {rc}, {rb}\n"
                )
            else:
                raise ValueError(f"Unreachable {bin_expr.op.type}")
            
            self.output.append(
                f"{label}:\n"
                f"    test {rc}, {rc}\n"
                "    setne al\n"
            )
            self.push_stack("al")
        else:
            raise ValueError(f"Unreachable {bin_expr.op.type}")

    def gen_expression(self, expression: NodeExpr) -> None:
        """
        generates an expression and pushes it on top of the stack
        """
        if isinstance(expression.var, NodeTerm):
            self.gen_term(expression.var)
        elif isinstance(expression.var, NodeBinExpr):
            self.gen_binary_expression(expression.var)
        else:
            raise ValueError("Unreachable")

    def gen_scope(self, scope: NodeScope) -> None:
        """
        generates all of the statements in a given scope
        """
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
            self.output.append(
                f"    jmp {end_label}\n"
                f"{label}:\n"
            )
            if pred.var.pred is not None:
                self.gen_if_predicate(pred.var.pred, end_label)
        elif isinstance(pred.var, NodeIfPredElse):
            self.output.append("    ;; --- else ---\n")
            self.gen_scope(pred.var.scope)
        else:
            raise ValueError("Unreachable")

    def add_variable(self, decl_stmt: NodeStmtDeclare, word_size: size_words, byte_size: size_bytes):
        """
        adds a VariableContext into the self.variables list
        """
        location: int = self.stack_size
        assert decl_stmt.ident.value is not None, "var name shouldn't be None here"
        self.variables.append(VariableContext(decl_stmt.ident.value, location, decl_stmt.type_, word_size, byte_size))

    def gen_decl(self, decl_stmt: NodeStmtDeclare):
        """
        generates a variable declaration
        """
        found_vars: tuple[VariableContext, ...] = tuple(
            filter(
                lambda x: x.name == decl_stmt.ident.value, 
                self.variables[self.scopes[-1]::]
            )
        )
        if found_vars:
            self.compiler_error("Value", f"variable has been already declared in this scope: {decl_stmt.ident.value}", decl_stmt.ident)

        if decl_stmt.type_.type == tt.INT_DEF:
            self.output.append("    ;; --- int var declaration ---\n")
            self.gen_expression(decl_stmt.expr)
            self.add_variable(decl_stmt, "DWORD", 4)
        elif decl_stmt.type_.type == tt.BOOL_DEF:
            self.output.append("    ;; --- bul var declaration ---\n")
            self.gen_expression(decl_stmt.expr)
            self.add_variable(decl_stmt, "BYTE", 1)
        elif decl_stmt.type_.type == tt.CHAR_DEF:
            self.output.append("    ;; --- char var declaration ---\n")
            self.gen_expression(decl_stmt.expr)
            self.add_variable(decl_stmt, "BYTE", 1)
        elif decl_stmt.type_.type == tt.STR_DEF:
            self.output.append("    ;; --- string var declaration ---\n")
            self.gen_expression(decl_stmt.expr)
            self.add_variable(decl_stmt, "STR", sum(self.stack_item_sizes[-1]))
        elif decl_stmt.type_.type == tt.ARRAY_TYPE:
            self.output.append("    ;; --- array var declaration ---\n")
            self.gen_expression(decl_stmt.expr)
            self.add_variable(decl_stmt, "STR", sum(self.stack_item_sizes[-1]))
        else:
            raise ValueError("Unreachable")
        
    def gen_reassign(self, reassign_stmt: NodeStmtReassign):
        """
        generates a var reassignment, increment and decrement
        """
        assert isinstance(reassign_stmt.var.ident.var, NodeTermIdent)
        found_vars: tuple[VariableContext, ...] = tuple(filter(lambda x: x.name == reassign_stmt.var.ident.var.ident.value, self.variables)) # type: ignore
        
        if isinstance(reassign_stmt.var, NodeStmtReassignEq):
            self.output.append("    ;; --- var reassign ---\n")
            var_ctx = found_vars[-1]

            if reassign_stmt.var.ident.index is not None:
                LEN_SIZE = 4
                ITEM_SIZE_B = 1
                self.gen_expression(reassign_stmt.var.ident.index)
                rb = "rbx"
                self.output.append(f"    xor rbx, rbx\n")
                self.pop_stack("ebx") # saves the offset

                offset = f"{rb} * {ITEM_SIZE_B}"
                location = var_ctx.loc - LEN_SIZE
                self.output.append(f"    mov rcx, [rbp - {location}]\n")
                self.gen_expression(reassign_stmt.var.rvalue)
                ra = self.get_reg(0)
                self.pop_stack(ra)
                self.output.append(f"    mov [rcx + {offset}], {ra}\n")
            else:
                # Normal reassign
                self.gen_expression(reassign_stmt.var.rvalue)
                if self.stack_item_sizes[-1] not in ([1], [2], [4], [8]):
                    # only runs for non primitive types
                    self.output.append(
                        f"    mov eax, [rbp - {self.stack_size}]\n"
                        f"    mov [rbp - {var_ctx.loc}], eax\n"
                        f"    mov rax, [rbp - {self.stack_size - 4}]\n"
                        f"    mov [rbp - {var_ctx.loc - 4}], rax\n"
                    )
                    self.stack_size -= sum(self.stack_item_sizes.pop())
                else:
                    ra = self.get_reg(0)
                    self.pop_stack(ra)
                    self.output.append(f"    mov [rbp - {var_ctx.loc}], {ra}\n")
        elif isinstance(reassign_stmt.var, (NodeStmtReassignInc, NodeStmtReassignDec)):
            self.output.append("    ;; --- var inc / dec ---\n")
            var_ctx = found_vars[-1]
            location, size_words = var_ctx.loc, var_ctx.size_w
            self.push_stack(f"{size_words} [rbp - {location}]") # QWORD 64 bits (word = 16 bits)
            ra = self.get_reg(0)
            self.pop_stack(ra)
            inc_or_dec = f"    inc {ra}\n" if isinstance(reassign_stmt.var, NodeStmtReassignInc) else f"    dec {ra}\n"
            self.output.append(
                inc_or_dec +
                f"    mov [rbp - {location}], {ra}\n"
            )
        else:
            raise ValueError("Unreachable")

    def gen_exit(self, exit_stmt: NodeStmtExit) -> None:
        """
        generates an exit syscall
        """
        self.output.append("    ;; --- exit ---\n")
        self.gen_expression(exit_stmt.expr)
        rdi = self.get_reg(5) # rdi / di is 5th register
        self.pop_stack(rdi)
        self.call_func("exit")

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
            self.output.append(
                f"    jmp {end_label}\n"
                f"{label}:\n"
            )
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
        self.output.append(
            f"    test {first_reg}, {first_reg}\n"
            f"    jz {end_label}\n"
        )

        self.gen_scope(while_stmt.scope)
        
        self.output.append(
            f"    jmp {reset_label}\n"
            f"{end_label}:\n"
        )
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
        self.output.append(
            f"    test {first_reg}, {first_reg}\n"
            f"    jz {end_label}\n"
        )

        self.output.append(
            f"    jmp {reset_label}\n"
            f"{end_label}:\n"
        )
        self.loop_end_labels.pop()

    def gen_for(self, for_stmt: NodeStmtFor) -> None:
        self.output.append("    ;; --- for loop ---\n")
        end_label = self.create_label("end")
        reset_label = self.create_label("rst")
        self.loop_end_labels.append(end_label)

        self.gen_decl(for_stmt.ident_def)

        self.output.append(f"{reset_label}:\n")

        self.gen_expression(for_stmt.condition)

        first_reg = self.get_reg(0)
        self.pop_stack(first_reg)
        self.output.append(
            f"    test {first_reg}, {first_reg}\n"
            f"    jz {end_label}\n"
        )

        self.gen_scope(for_stmt.scope)
        
        self.gen_reassign(for_stmt.ident_assign)

        self.output.append(
            f"    jmp {reset_label}\n"
            f"{end_label}:\n"
        )
        assert len(self.stack_item_sizes[-1]) == 1, "index should be an integer" 
        self.stack_size -= self.stack_item_sizes.pop()[0] # does this to remove the variable after the i loop ends
        self.variables.pop()
        self.loop_end_labels.pop()

    def gen_print(self, print_stmt: NodeStmtPrint) -> None:
        """
        generates a print syscall and cleaning up the stack
        """
        if print_stmt.cont_type == CHAR_DEF:
            self.output.append("    ;; --- print char ---\n")
            self.gen_expression(print_stmt.content)

            self.output.append(f"    lea rsi, [rbp - {self.stack_size}]\n")
            self.call_func("print_char")
            # it removes the printed expression because it causes a mess in the stack when looping
            self.stack_size -= sum(self.stack_item_sizes.pop() + self.stack_padding.pop())
        elif print_stmt.cont_type == STR_DEF:
            self.output.append("    ;; --- print str ---\n")
            self.gen_expression(print_stmt.content)
            LEN_SIZE = 4
            self.output.append(
                f"    mov rsi, [rbp - {self.stack_size - LEN_SIZE}]\n"
                f"    mov edx, [rbp - {self.stack_size}]\n"
            )

            self.call_func("print_str")
            # it removes the printed expression because it causes a mess in the stack when looping
            self.stack_size -= sum(self.stack_item_sizes.pop() + self.stack_padding.pop())

    def gen_break(self, break_stmt: NodeStmtBreak) -> None:
        """
        adds a jump to the end of the loop if it exists, if not in a loop throws a compiler error
        """
        if self.loop_end_labels:
            self.output.append(
                "    ;; --- break --- \n"
                f"    jmp {self.loop_end_labels[-1]}\n"
            )
        else:
            self.compiler_error("Syntax", "cant break out of a loop when not inside one", break_stmt.break_tkn)

    def gen_statement(self, statement: NodeStmt) -> None:
        """
        generates a statement based on the node passed in
        """
        gen_func: Callable | None = self.map_generate_func.get(statement.stmt_var.__class__)
        
        if gen_func is not None: #can be None for NodeStmtEmpty
            gen_func(statement.stmt_var)
        elif isinstance(statement.stmt_var, NodeStmtEmpty):
            pass
        else:
            raise ValueError("Unreachable") 

    def gen_program(self) -> list[str]:
        """
        generates the whole assembly based on the nodes that are given,
        returns a list of strings that contains the assembly instructions
        """
        self.output.append(
            "format ELF64 executable 3\nsegment readable executable\nentry _start\n"
            "_start:\n    mov rbp, rsp\n"
        )

        for stmt in self.main_program.stmts:
            assert stmt is not None, "None statement shouldn't make it here"
            self.gen_statement(stmt)

        self.output.append("    ;; --- default exit ---\n    mov rax, 60\n    mov rdi, 0\n    syscall\n" )
        self.add_funcs()
        if self.section_data:
            self.output.append("segment readable writeable\n")
            self.output.extend(self.section_data)
        return self.output
