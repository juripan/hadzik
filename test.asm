global _start
_start:
    mov rax, 12
    push rax
    mov rax, 1
    push rax
    mov rax, 0
    push rax
    ;if block
    mov rax, 12
    push rax
    push QWORD [rsp + 24]
    mov rax, 1
    push rax
    pop rax
    pop rbx
    cmp rax, rbx
    setc al
    movzx rax, al
    push rax
    pop rax
    pop rbx
    cmp rax, rbx
    setc al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label1
    ;reassigning a variable
    mov rax, 1
    push rax
    pop rax
    mov [rsp + 0], rax
    ;/reassigning a variable
    add rsp, 0
label1:
    ;/if block
    ;if block
    push QWORD [rsp + 16]
    push QWORD [rsp + 16]
    pop rax
    pop rbx
    cmp rax, rbx
    seta al
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz label2
    ;reassigning a variable
    mov rax, 2
    push rax
    pop rax
    mov [rsp + 0], rax
    ;/reassigning a variable
    add rsp, 0
label2:
    ;/if block
    push QWORD [rsp + 0]
    ; manual exit (vychod)
    mov rax, 60
    pop rdi
    syscall
    ; default exit
    mov rax, 60
    mov rdi, 0
    syscall