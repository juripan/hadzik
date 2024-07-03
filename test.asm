global _start
_start:
    ; integer eval
    mov rax, 0
    push rax
    ; integer eval
    mov rax, 0
    push rax
    pop rax
    test rax, rax
    jz label1
    ; integer eval
    mov rax, 1
    push rax
    pop rax
    mov [rsp + 0], rax
    ; scope end
    add rsp, 0
    jmp label2
label1:
    ; integer eval
    mov rax, 0
    push rax
    pop rax
    test rax, rax
    jz label3
    ; integer eval
    mov rax, 14
    push rax
    pop rax
    mov [rsp + 0], rax
    ; scope end
    add rsp, 0
    jmp label2
label3:
    ; integer eval
    mov rax, 12
    push rax
    pop rax
    mov [rsp + 0], rax
    ; scope end
    add rsp, 0
label2:
    ; integer eval
    mov rax, 55
    push rax
    pop rax
    mov [rsp + 0], rax
    ; identifier eval
    push QWORD [rsp + 0]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall