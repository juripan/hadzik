global _start
_start:
    mov rax, 0
    push rax
    push QWORD [rsp + -8]
    mov rax, 1
    push rax
    pop rax
    pop rbx
    add rax, rbx
    push rax
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