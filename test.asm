section .data
section .bss
section .text
    global _start
_start:
    push -12
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
    push 121
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
    ;for loop
    push 0
label4:
    push 5
    push QWORD [rsp + 8]
    pop rax
    pop rbx
    cmp rax, rbx
    setl al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label3
    push 60
    push QWORD [rsp + 8]
    pop rax
    pop rbx
    add rax, rbx
    push rax
    ; printing
    mov rax, 1
    mov rdi, 1
    mov rsi, rsp
    mov rdx, 1
    syscall
    add rsp, 8
    ; /printing
    add rsp, 0
    ;reassigning a variable
    push QWORD [rsp + 0]
    pop rax
    inc rax
    mov [rsp + 0], rax
    ;/reassigning a variable
    jmp label4
label3:
    add rsp, 8
    ;/for loop
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall