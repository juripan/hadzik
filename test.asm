section .data
section .bss
section .text
    global _start
_start:
    mov rax, 11
    push rax
    ;for loop
    mov rax, 0
    push rax
label2:
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
    jz label1
    ;reassigning a variable
    push QWORD [rsp + 0]
    pop rax
    add rax, 1
    mov [rsp + 0], rax
    ;/reassigning a variable
    ;for loop
    mov rax, 0
    push rax
label4:
    mov rax, 2
    push rax
    push QWORD [rsp + 8]
    pop rax
    pop rbx
    cmp rax, rbx
    setle al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label3
    ;reassigning a variable
    push QWORD [rsp + 0]
    pop rax
    add rax, 1
    mov [rsp + 0], rax
    ;/reassigning a variable
    ;reassigning a variable
    mov rax, 1
    push rax
    push QWORD [rsp + 24]
    pop rax
    pop rbx
    add rax, rbx
    push rax
    pop rax
    mov [rsp + 16], rax
    ;/reassigning a variable
    add rsp, 0
    jmp label4
label3:
    add rsp, 8
    ;/for loop
    add rsp, 0
    jmp label2
label1:
    add rsp, 8
    ;/for loop
    push QWORD [rsp + 0]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall