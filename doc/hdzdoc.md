# HADZIK DOCUMENTATION

## Variables
### Declaration
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
+ lancok \*ident\* = \*value\* - creates a 32-bit length and a 64-bit pointer to the string on the stack, string itself is located on the stack as well
```
lancok greeting = "ahoj\n"
```
*Note: strings are passed around as a pointer + length on the stack, so when reassigning it doesn't create a copy or can create memory bugs when the string is deallocated*

#### Type inference
Types can also be automatically inferred using the `naj` keyword:
+ naj \*ident\* = \*value\* - creates a variable with an inferred type by the typechecker on the stack
```
naj grade = 'D'
```
#### Constants
Constants can be declared by using the `furt` keyword, they cannot be reassigned or modified
+ furt \*type\* \*ident\* = \*value\* - creates a constant with a give type on the stack
```
furt cif PI = 3
```
You can also let it infer the type by leaving out the type in the declaration of the constant
```
furt E = 2
```
### Reassignment
+ \*ident\* = \*value\* - assigns a different value fo the same type to a variable
```
x = nepravda
```
### Indexing
+ \*ident\*\[*n*\] - accesses the *n-th* value in the variable starting from 0, variable must be of indexable type and n must be an integer, supports reading and writing
```
greeting[3] = 'p'
znak a = greeting[0]
```

## Operations
### Numeric - (number) -> number
#### Mathematical
+ \*number\* + \*number\* - adds two numbers together
+ \*number\* - \*number\* - subtracts a number from another
+ \*number\* \* \*number\* - multiplies two numbers together
+ \*number\* / \*number\* - divides a number by another (currently whole number division)
+ \*number\* % \*number\* - gives a remainder of division (whole number division)
+ -\*number\* - negates the number given
#### Bitwise
+ ~\*number\* - bitwise NOT
+ \*number\* & \*number\* - bitwise AND
+ \*number\* | \*number\* - bitwise OR
+ \*number\* ^ \*number\* - bitwise XOR
+ \*number\* << \*number\* - bitwise shift left
+ \*number\* >> \*number\* - bitwise shift right
### Predicative - (number | char) -> boolean
+ \*number\* == \*number\* - equal
+ \*number\* != \*number\* - not equal
+ \*number\* < \*number\* - less than
+ \*number\* > \*number\* - larger than
+ \*number\* <= \*number\* - less than or equal
+ \*number\* >= \*number\* - larger than or equal
### Logical - (boolean) -> boolean
+ ne \*boolean\* - logical NOT
+ \*boolean\* aj \*boolean\* - logical AND
+ \*boolean\* abo \*boolean\* - logical OR

## Built-ins
+ vychod(\*int\*) - exits the program with the passed in exit code
```
vychod(5)
```
+ hutor(\*value\*) - prints the given string or char into stdin via system call
```
hutor('a')
hutor("cau")
```
### Typecasting
+ \*type\*(\*value\*) - changes the type of the value to the desired type
```
znak A = znak(65)
```

## Control flow
### If + Elseif + Else
+ kec \*condition\* \*scope\* - if statement
*note: conditions can be a boolean or an arithmetic expression*
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
