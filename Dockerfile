#NOTE: this dockerfile is run maling a version of the src directory on the /app docker run -v <src dir path>:/app <image name>

FROM ubuntu
# maybe it should use alpine instead

RUN apt-get update

RUN apt-get install -y nasm binutils

RUN apt-get install -y python3

ENV LANG=en_US.utf8

COPY tools/start.sh .

CMD ["./start.sh"]
