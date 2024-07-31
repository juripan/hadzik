
# HADZIK
Programming language with keywords based on east slovak dialect.

file extension: **.hdz**

Strings use " "
chars use ' '

Scopes are declared by curly braces

Enter ends statements instead of using ';' to end statements

All current design principles are subject to change.


## Docker:
The start.sh file located in the tools directory is used by the Dockerfile when creating a container

The container creates a volume of the source directory on the /app directory inside the docker container so it can access the src folder and modify its content

**NOTE: use the full file paths on windows** 
```
docker build -t <image name> <Dockerfile directory>
docker run -v <src dir path>:/app <image name>
```

## Credits:
name of the programming language by: Miška Mašlonková
