# HADZIK DOCUMENTATION

## Variables
### Declaration:
+ cif \*ident\* = \*value\* - creates a 32-bit integer with a given value on the stack
```
cif y = 5
```
+ bul \*ident\* = \*value\* - creates a 8-bit boolean with a given value on the stack
```
bul x = pravda
```
+ znak \*ident\* = \*value\* - creates a 8-bit char with a given value on the stack
```
znak d = 'd'
```
+ lancok \*ident\* = \*value\* - creates a 32-bit size and a 32-bit pointer to the string on the stack, string itself is located in the data section
```
lancok greeting = "ahoj\n"
```
#### Type inference:
Types can also be automatically inferred:
+ naj \*ident\* = \*value\* - creates a variable with an inferred type by the typechecker on the stack
```
naj grade = 'D'
```
#### Constants:
Constants can be declared by using the `furt` keyword, they cannot be reassigned or modified
+ furt \*type\* \*ident\* = \*value\* - creates a constant with a give type on the stack
```
furt cif PI = 3
```
You can also let it infer the type by leaving out the type in the declaration of the constant
```
furt E = 2
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
+ hutor(\*char\*) - prints the given string or char into stdin via system call
```
hutor('a')
hutor("cau")
```

## Control flow
### If + Elseif + Else
+ kec \*condition\* \*scope\* - if statement
note: conditions can be a boolean or arithmetic expression
+ ikec \*condition\* \*scope\* - else-if statement
+ inac \*scope\* - else statement 
```
cif count = 10
cif x = 15

kec count == 5 {
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
