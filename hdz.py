import sys
import os

from hdzlexer import Tokenizer
from hdzparser import Parser
from hdzgenerator import Generator


filename: str = sys.argv[1]

with open("./" + filename, "r") as f:
    content: str = f.read()

print(tokens := Tokenizer(content).tokenize())
print(parse_tree := Parser(tokens, content).parse_program())
print(final_asm := Generator(parse_tree, content).generate_program())

cropped_filename = filename[:4]

with open("./" + cropped_filename + ".asm", "w") as f:
    f.write(final_asm)

os.system("nasm -felf64 " + cropped_filename + ".asm")
os.system("ld " + cropped_filename + ".o -o " + cropped_filename)
