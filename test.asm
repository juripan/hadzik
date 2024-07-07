global _start
_start:
    mov rax, 1
    push rax
    mov rax, 1
    push rax
    pop rax
    pop rbx
    add rax, rbx
    push rax
    mov rax, 12
    push rax
    add rsp, 0
    ;if block
    mov rax, 2
    push rax
    mov rax, 1
    push rax
    pop rax
    pop rbx
    cmp rax, rbx
    sete al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label1
    ;if block
    mov rax, 12
    push rax
    push QWORD [rsp + 8]
    pop rax
    pop rbx
    cmp rax, rbx
    sete al
    movzx rax, al
    push rax
    pop rbx
    xor eax, eax
    test rbx, rbx
    sete al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label2
    push QWORD [rsp + 8]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    add rsp, 0
    jmp label3
label2:
    ;else
    ;reassigning a variable
    mov rax, 2
    push rax
    mov rax, 11
    push rax
    mov rax, 12
    push rax
    pop rax
    pop rbx
    add rax, rbx
    push rax
    pop rax
    pop rbx
    mul rbx
    push rax
    pop rax
    mov [rsp + 8], rax
    ;/reassigning a variable
    push QWORD [rsp + 8]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    add rsp, 0
    ;/else
label3:
    ;/if block
    add rsp, 0
    jmp label4
label1:
    ;elif
    mov rax, -11
    push rax
    mov rax, -12
    push rax
    pop rax
    pop rbx
    cmp rax, rbx
    setge al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label5
    ;reassigning a variable
    mov rax, 4
    push rax
    mov rax, 89
    push rax
    pop rax
    pop rbx
    add rax, rbx
    push rax
    pop rax
    mov [rsp + 8], rax
    ;/reassigning a variable
    add rsp, 0
    jmp label4
label5:
    ;/elif
    ;elif
    mov rax, 24
    push rax
    mov rax, 2
    push rax
    mov rax, 12
    push rax
    pop rax
    pop rbx
    mul rbx
    push rax
    pop rax
    pop rbx
    cmp rax, rbx
    sete al
    movzx rax, al
    push rax
    mov rax, 10
    push rax
    mov rax, 11
    push rax
    pop rax
    pop rbx
    cmp rax, rbx
    sete al
    movzx rax, al
    push rax
    pop rax
    pop rbx
    and rax, rbx
    push rax
    pop rbx
    xor eax, eax
    test rbx, rbx
    sete al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label6
    ;reassigning a variable
    mov rax, 6
    push rax
    mov rax, 15
    push rax
    pop rax
    pop rbx
    mul rbx
    push rax
    pop rax
    mov [rsp + 8], rax
    ;/reassigning a variable
    add rsp, 0
    jmp label4
label6:
    ;/elif
    ;elif
    mov rax, 2
    push rax
    mov rax, 24
    push rax
    pop rax
    pop rbx
    div rbx
    push rax
    mov rax, 12
    push rax
    pop rax
    pop rbx
    cmp rax, rbx
    sete al
    movzx rax, al
    push rax
    mov rax, 1
    push rax
    mov rax, 11
    push rax
    pop rax
    pop rbx
    cmp rax, rbx
    sete al
    movzx rax, al
    push rax
    pop rax
    pop rbx
    or rax, rbx
    push rax
    pop rax
    test rax, rax
    jz label7
    ;reassigning a variable
    mov rax, 5
    push rax
    mov rax, 5
    push rax
    pop rax
    pop rbx
    mul rbx
    push rax
    pop rax
    mov [rsp + 8], rax
    ;/reassigning a variable
    add rsp, 0
    jmp label4
label7:
    ;/elif
    ;else
    ;reassigning a variable
    mov rax, -9
    push rax
    mov rax, -18
    push rax
    pop rax
    pop rbx
    mul rbx
    push rax
    pop rax
    mov [rsp + 8], rax
    ;/reassigning a variable
    add rsp, 0
    ;/else
label4:
    ;/if block
    push QWORD [rsp + 8]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall