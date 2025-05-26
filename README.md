
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
$ python3 <path to `hdzc`> <path to your code>.hdz [flags] [dst path if using -n flag]
```
Or you can run it as an executable like this:
```
$ ./<path to `hdzc`> <path to your code>.hdz [flags] [dst path if using -n flag]
```

## Flags:
Flags that are used when running the compiler in the console (more are going to be added in the future)

+ -s - switches on the east slovak error messages
```
$ python3 hdzc path/file.hdz -s
```

+ -r - after compilation is done runs the compiled file and prints its output
```
$ python3 hdzc path/file.hdz -r
```

+ -n - determine a path and name of the compiled file
```
$ python3 hdzc path/file.hdz -n new_path/file2
```

+ -d - dumps all of the compiler debug information available to the console
```
$ python3 hdzc path/file.hdz -d
```

+ --help - displays user manual
```
$ python3 hdzc --help
```

Order of flags doesn't matter just the order of paths:
```
$ python3 hdzc path/file.hdz -s -r new_path/file2 -n
```


## Dependencies:
all of the dependencies are listed in the Docker file and source code files but for more transparency I will list them here also
+ Python 3.12.3
+ libraries: sys, os, dataclasses, typing
+ NASM version 2.16.01
+ GNU ld 2.42

## Priorities:
+ typecasting
+ for loop rewrite
+ macros

## Docker:
To run this project in a docker you first need to install docker and then run these commands

**NOTE: use the full file paths on windows** 
```
$ docker build -t <image name> <Dockerfile directory>
$ docker run -it -v <src dir path>:/app <image name>
```
The container creates a volume of the source directory on the /app directory inside the docker container so it can access the src folder and modify its content

-it flag makes the container console accessible so you can run the start.sh file yourself or run any commands in the container until you close it

## Credits:
name of the programming language by: Miška Mašlonková
