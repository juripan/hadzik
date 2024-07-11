section .data
section .bss
section .text
    global _start
_start:
    mov rax, -12
    push rax
    mov rax, 8
    push rax
    mov rax, 0
    push rax
    mov rax, 0
    push rax
    pop rax
    pop rbx
    mov rcx, rax
    test rbx, rbx
    cmovnz rcx, rbx
    test rcx, rcx
    setne al
    movzx rax, al
    push rax
    pop rax
    pop rbx
    mov rcx, rax
    test rbx, rbx
    cmovnz rcx, rbx
    test rcx, rcx
    setne al
    movzx rax, al
    push rax
    pop rbx
    xor eax, eax
    test rbx, rbx
    sete al
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