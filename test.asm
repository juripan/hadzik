global _start
_start:
    mov rax, 1
    push rax
    mov rax, 12
    push rax
    add rsp, 0
    ;if block
    mov rax, 2
    push rax
    push QWORD [rsp + 16]
    pop rax
    pop rbx
    cmp rax, rbx
    sete al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label1
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
    jmp label2
label1:
    ;elif
    mov rax, 55
    push rax
    mov rax, 12
    push rax
    pop rax
    pop rbx
    cmp rax, rbx
    setge al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label3
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
    jmp label2
label3:
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
    mov rax, 11
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
    jz label4
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
    jmp label2
label4:
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
label2:
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