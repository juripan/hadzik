section .data
section .bss
section .text
    global _start
_start:
    push 7
    push 11
    push QWORD [rsp + 8]
    ;reassigning a variable
    push QWORD [rsp + 16]
    pop rax
    inc rax
    mov [rsp + 16], rax
    ;/reassigning a variable
    ;while loop
label2:
    push QWORD [rsp + 16]
    pop rax
    test rax, rax
    jz label1
    ;reassigning a variable
    push QWORD [rsp + 16]
    pop rax
    dec rax
    mov [rsp + 16], rax
    ;/reassigning a variable
    add rsp, 0
    jmp label2
label1:
    ;/while loop
    ;reassigning a variable
    push QWORD [rsp + 16]
    pop rax
    dec rax
    mov [rsp + 16], rax
    ;/reassigning a variable
    push QWORD [rsp + 16]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall