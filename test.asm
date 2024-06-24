global _start
_start:
    ; integer eval
    mov rax, 12
    push rax
    ; adding
    ; integer eval
    mov rax, 24
    push rax
    ; adding
    ; integer eval
    mov rax, 1
    push rax
    ; adding
    ; integer eval
    mov rax, 11
    push rax
    ; identifier eval
    push QWORD [rsp + 24]
    pop rax
    pop rbx
    add rax, rbx
    push rax
    pop rax
    pop rbx
    add rax, rbx
    push rax
    pop rax
    pop rbx
    add rax, rbx
    push rax
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