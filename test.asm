global _start
_start:
    ; integer eval
    mov rax, 3
    push rax
    ; integer eval
    mov rax, 8
    push rax
    ; adding
    pop rax
    pop rbx
    add rax, rbx
    push rax
    ; integer eval
    mov rax, 3
    push rax
    ; integer eval
    mov rax, 0
    push rax
    ; subtracting
    pop rax
    pop rbx
    sub rax, rbx
    push rax
    ; integer eval
    mov rax, 8
    push rax
    ; integer eval
    mov rax, 0
    push rax
    ; subtracting
    pop rax
    pop rbx
    sub rax, rbx
    push rax
    ; multiplying
    pop rax
    pop rbx
    mul rbx
    push rax
    ; identifier eval
    push QWORD [rsp + 0]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; identifier eval
    push QWORD [rsp + 8]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall