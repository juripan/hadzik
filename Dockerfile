# maybe use alpine instead
FROM ubuntu

RUN apt-get update

RUN apt-get install -y nasm binutils

RUN apt-get install -y python3

ENV LANG=en_US.utf8

COPY src .

COPY tools/start.sh .

CMD ["./start.sh"]
