#!/bin/sh

cd /app

python3 hdzc test.hdz
./test
echo 'Exit code: '$?
