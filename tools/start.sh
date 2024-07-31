#!/bin/bash

cd /app

python3 hdz.py test.hdz
nasm -felf64 test.asm -o test.o
ld test.o -o test
./test
echo 'Exit code: '$?
