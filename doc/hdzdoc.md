# HADZIK DOCUMENTATION

## Variables
### Declaration:
+ cis \*ident\* = \*value\* - creates a 32-bit integer with a given value on the stack
```
cis y = 5
```
+ bul \*ident\* = \*value\* - creates a 8-bit boolean with a given value on the stack
```
bul x = pravda
```
### Reassignment:
+ \*ident\* = \*value\* - assigns a different value fo the same type to a variable
```
x = nepravda
```

## Built-ins
+ vychod(\*int\*) - exits the program with the passed in exit code
```
vychod(5)
```
+ hutor(\*char\*) - prints the given char into stdin via system call
```
hutor('a')
```

## Control flow
### If + Elseif + Else
+ kec \*condition\* \*scope\* - if statement
+ ikec \*condition\* \*scope\* - else-if statement
+ inac \*scope\* - else statement 
```
kec y == 5 {
    hutor('a')
} ikec x {
    hutor('b')
} inac {
    hutor('c')
}
```
### While and Do-While loops 
+ kim \*condition\* \*scope\*
```
kim y < 10 {
    y++
}
```
+ zrob \*scope\* kim \*condition\*
```
zrob {
    y--
} kim y > 5
```
