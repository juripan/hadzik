#!/bin/sh

cd /app

python3 hdz.py test.hdz
./test
echo 'Exit code: '$?
