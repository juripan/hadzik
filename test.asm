section .data
section .bss
section .text
    global _start
_start:
    mov rax, 7
    push rax
    mov rax, 11
    push rax
    push QWORD [rsp + 8]
    ;reassigning a variable
    push QWORD [rsp + 16]
    pop rax
    add rax, 1
    mov [rsp + 16], rax
    ;/reassigning a variable
    ;if block
    mov rax, 1
    push rax
    pop rax
    test rax, rax
    jz label1
    ;reassigning a variable
    push QWORD [rsp + 16]
    pop rax
    add rax, 1
    mov [rsp + 16], rax
    ;/reassigning a variable
    add rsp, 0
label1:
    ;/if block
    ;for loop
    mov rax, 0
    push rax
label3:
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
    jz label2
    ;reassigning a variable
    push QWORD [rsp + 0]
    pop rax
    add rax, 1
    mov [rsp + 0], rax
    ;/reassigning a variable
    ;reassigning a variable
    push QWORD [rsp + 8]
    pop rax
    add rax, 1
    mov [rsp + 8], rax
    ;/reassigning a variable
    add rsp, 0
    jmp label3
label2:
    add rsp, 8
    ;/for loop
    ;for loop
    mov rax, 0
    push rax
label5:
    mov rax, 2
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
    jz label4
    ;reassigning a variable
    push QWORD [rsp + 0]
    pop rax
    add rax, 1
    mov [rsp + 0], rax
    ;/reassigning a variable
    ;do while loop
label7:
    ;reassigning a variable
    push QWORD [rsp + 16]
    pop rax
    sub rax, 1
    mov [rsp + 16], rax
    ;/reassigning a variable
    add rsp, 0
    mov rax, 11
    push rax
    push QWORD [rsp + 24]
    pop rax
    pop rbx
    cmp rax, rbx
    setge al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label6
    jmp label7
label6:
    ;/do while loop
    add rsp, 0
    jmp label5
label4:
    add rsp, 8
    ;/for loop
    push QWORD [rsp + 8]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall