section .data
section .bss
section .text
    global _start
_start:
    mov rax, -12
    push rax
    ;if block
    mov rax, 0
    push rax
    mov rax, 2
    push rax
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
    mov rax, 121
    push rax
    ; printing
    mov rax, 1
    mov rdi, 1
    mov rsi, rsp
    mov rdx, 1
    syscall
    add rsp, 8
    ; /printing
    mov rax, 10
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
    jmp label2
label1:
    ;else
    mov rax, 110
    push rax
    ; printing
    mov rax, 1
    mov rdi, 1
    mov rsi, rsp
    mov rdx, 1
    syscall
    add rsp, 8
    ; /printing
    mov rax, 10
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
    ;/else
label2:
    ;/if block
    ;for loop
    mov rax, 0
    push rax
label4:
    mov rax, 5
    push rax
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
    mov rax, 60
    push rax
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