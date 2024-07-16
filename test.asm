section .data
section .bss
section .text
    global _start
_start:
    push 12
    ;if block
    push 0
    push 2
    push QWORD [rsp + 16]
    pop rax
    pop rbx
    mov rdx, 0
    cqo
    idiv rbx
    push rdx
    pop rax
    pop rbx
    cmp rax, rbx
    sete al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label1
    push 97
    ; printing
    mov rax, 1
    mov rdi, 1
    mov rsi, rsp
    mov rdx, 1
    syscall
    add rsp, 8
    ; /printing
    push 10
    ; printing
    mov rax, 1
    mov rdi, 1
    mov rsi, rsp
    mov rdx, 1
    syscall
    add rsp, 8
    ; /printing
    add rsp, 0
    jmp label2
label1:
    ;else
    push 110
    ; printing
    mov rax, 1
    mov rdi, 1
    mov rsi, rsp
    mov rdx, 1
    syscall
    add rsp, 8
    ; /printing
    push 10
    ; printing
    mov rax, 1
    mov rdi, 1
    mov rsi, rsp
    mov rdx, 1
    syscall
    add rsp, 8
    ; /printing
    add rsp, 0
    ;/else
label2:
    ;/if block
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall