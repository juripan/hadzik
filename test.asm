global _start
_start:
    mov rax, 60
    mov rdi, 78
    syscall
    mov rax, 60
    mov rdi, 12
    syscall

    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall