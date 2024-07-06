global _start
_start:
    mov rax, 1
    push rax
    mov rax, 12
    push rax
    push QWORD [rsp + 8]
    pop rax
    pop rbx
    cmp rax, rbx
    setge al
    movzx rax, al
    push rax
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall