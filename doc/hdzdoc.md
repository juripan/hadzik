# HADZIK DOCUMENTATION

## Variables
### Declaration:
+ naj \*ident\* = \*value\* - creates a 32-bit integer with a given value on the stack
```
naj y = 5
```
+ bul \*ident\* = \*value\* - creates a 8-bit boolean with a given value on the stack
```
bul x = pravda
```
### Reassignment:
+ \*ident\* = \*value\* - assigns a different value to a variable
```
x = nepravda
```

## Built-ins
+ vychod(\*exit-code\*) - exits the program with the passed in exit code
```
vychod(5)
```
+ hutor(\*char\*) - prints the given char into stdin via system call
```
hutor('a')
```
+ ...
