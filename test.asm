section .data
section .bss
section .text
    global _start
_start:
    mov rax, -12
    push rax
    mov rax, 8
    push rax
    mov ax, 0
    push ax
    ;if block
    push WORD [rsp + 0]
    pop ax
    test ax, ax
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
    jmp label2
label1:
    ;elif
    push QWORD [rsp + 10]
    pop ax
    test ax, ax
    jz label3
    mov rax, 51
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
    jmp label2
label3:
    ;/elif
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
    ;/else
label2:
    ;/if block
    ;for loop
    mov rax, 0
    push rax
label5:
    mov rax, 5
    push rax
    push QWORD [rsp + 8]
    pop rax
    pop rbx
    cmp rax, rbx
    setl al
    push ax
    pop ax
    test ax, ax
    jz label4
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
    ;reassigning a variable
    push QWORD [rsp + 0]
    pop rax
    inc rax
    mov [rsp + 0], rax
    ;/reassigning a variable
    jmp label5
label4:
    add rsp, 8
    ;/for loop
    ;while loop
label7:
    mov rax, 1
    push rax
    push QWORD [rsp + 10]
    pop rax
    pop rbx
    cmp rax, rbx
    setg al
    push ax
    pop ax
    test ax, ax
    jz label6
    ;reassigning a variable
    push QWORD [rsp + 2]
    pop rax
    dec rax
    mov [rsp + 2], rax
    ;/reassigning a variable
    jmp label7
label6:
    ;/while loop
    push QWORD [rsp + 2]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall