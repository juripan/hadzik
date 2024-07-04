global _start
_start:
    mov rax, 0
    push rax
    mov rax, 0
    push rax
    mov rax, 5
    push rax
    pop rax
    pop rbx
    cmp rax, rbx
    jne label1
    mov rax, 11
    push rax
    pop rax
    mov [rsp + 0], rax
    add rsp, 0
    jmp label2
label1:
    mov rax, 1
    push rax
    pop rax
    test rax, rax
    jz label3
    mov rax, 14
    push rax
    pop rax
    mov [rsp + 0], rax
    add rsp, 0
    jmp label2
label3:
    mov rax, 12
    push rax
    pop rax
    mov [rsp + 0], rax
    add rsp, 0
label2:
    push QWORD [rsp + 0]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    mov rax, 12
    push rax
    mov rax, 1
    push rax
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall