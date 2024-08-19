
# HADZIK
Programming language with keywords based on east slovak dialect.

file extension: **.hdz**

Strings use " "
chars use ' '

Scopes are declared by curly braces

Enter ends statements instead of using ';' to end statements

All current design principles are subject to change.

## Tags:
Tags that are used when running the compiler in the console

+ -s - switches on the east slovak error messages
+ more are going to be added in the future

## Docker:
To run this project in a docker you first need to install docker and then run these commands

**NOTE: use the full file paths on windows** 
```
docker build -t <image name> <Dockerfile directory>
docker run -it -v <src dir path>:/app <image name>
```
The container creates a volume of the source directory on the /app directory inside the docker container so it can access the src folder and modify its content

-it flag makes the container console acessible so you can run the start.sh file yourself or run any commands in the container until you close it

## Credits:
name of the programming language by: Miška Mašlonková
