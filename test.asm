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
    add rax, 1
    mov [rsp + 16], rax
    ;/reassigning a variable
    push QWORD [rsp + 0]
    push QWORD [rsp + 24]
    push QWORD [rsp + 24]
    pop rax
    pop rbx
    add rax, rbx
    push rax
    pop rax
    pop rbx
    add rax, rbx
    push rax
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall