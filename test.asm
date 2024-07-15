section .data
section .bss
section .text
    global _start
_start:
    push 65
    push 0
    push 12
    ;for loop
    push 0
label2:
    push 10
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
    inc rax
    mov [rsp + 0], rax
    ;/reassigning a variable
    ;reassigning a variable
    push QWORD [rsp + 16]
    push QWORD [rsp + 16]
    pop rax
    pop rbx
    add rax, rbx
    push rax
    pop rax
    mov [rsp + 16], rax
    ;/reassigning a variable
    push 30
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
    jmp label2
label1:
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