#NOTE: this dockerfile is run making a version of the src directory on the /app docker run -it -v <src dir path>:/app <image name>

FROM alpine

RUN apk add --no-cache binutils

RUN apk add --no-cache nasm

RUN apk add --no-cache python3

COPY tools/start.sh .
