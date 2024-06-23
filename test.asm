global _start
_start:
    mov rax, 3
    push rax
    push QWORD [rsp + 0]
    mov rax, 12
    push rax
    push QWORD [rsp + 0]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall