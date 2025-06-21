
# HADZIK

__This language is in its infancy. All current design principles are subject to change.__

A programming language with keywords based on east slovak dialect.  
Heavily inspired by Python and C.
For now only compiles to x86_64 linux assembly.  

File extension: **.hdz**

Strings use double quotes ("). 
Chars use single quotes (').
Scopes are declared by curly braces.  
Newline ends statements instead of semicolon.

## Quick start:
You can run the compiler as a python script like this:
```
$ python3 hdzc src_code [-h] [-s] [-n DEST] [-c] [-r] [-d]
```
Or you can run it as an executable like this:
```
$ ./hdzc src_code [-h] [-s] [-n DEST] [-c] [-r] [-d]
```

## Flags:
Flags that are used when running the compiler in the console (more are going to be added in the future)

+ -s - switches on the east slovak error messages
```
$ python3 hdzc path/file.hdz -s
```

+ -r - runs the compiled file and prints its output after compilation is done
```
$ python3 hdzc path/file.hdz -r
```

+ -n - determine a path and name of the compiled file
```
$ python3 hdzc path/file.hdz -n new_path/file2
```

+ -d - dumps all of the compiler debug information available into a log file and the stack info into the console
```
$ python3 hdzc path/file.hdz -d
```

+ -c - removes all of the log statements printed during compilation
```
$ python3 hdzc path/file.hdz -c
```

+ -h, --help - displays user manual
```
$ python3 hdzc --help
```

Order of flags doesn't matter just the order of paths:
```
$ python3 hdzc path/file.hdz -s -r new_path/file2 -n
```


## Dependencies:
+ Python 3.12.3
+ FASM version 1.73.32

## Priorities:
+ typecasting (full implementation)
+ for loop rewrite
+ macros (and some macro safety too)

## Credits:
name of the programming language by: Miška Mašlonková
