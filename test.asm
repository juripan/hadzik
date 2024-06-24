global _start
_start:
    ; integer eval
    mov rax, 3
    push rax
    ; identifier eval
    push QWORD [rsp + 0]
    ; integer eval
    mov rax, 12
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