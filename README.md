
# HADZIK
A programming language with keywords based on east slovak dialect.
Heavily inspired by Python and C programming languages
For now only compiles to x86_64 linux assembly

File extension: **.hdz**

Strings use " "
Chars use ' '

Scopes are declared by curly braces

'\n' ends statements instead of using ';' to end statements

All current design principles are subject to change

## Quick start:
```
$ python3 <path to 'hdz.py'> <path to your '.hdz' file>
```

## Flags:
Flags that are used when running the compiler in the console

+ -s - switches on the east slovak error messages
+ more are going to be added in the future

## Dependencies:
all of the dependencies are listed in the Docker file but for more transparency I will list them here also
+ Python 3.12.3
+ libraries: sys, os, collections
+ NASM version 2.16.01
+ GNU ld 2.42

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
