import sys
import os

from hdzlexer import Tokenizer
from hdzparser import Parser
from hdzgenerator import Generator


filename: str = sys.argv[1]

if not filename.endswith(".hdz"):
    print("file extension is missing or invalid (file extension must be .hdz)")
    exit(1)

with open("./" + filename, "r") as f:
    content: str = f.read()

tokens = Tokenizer(content).tokenize()
print(tokens)
parse_tree = Parser(tokens, content).parse_program()
print(parse_tree)
final_asm = Generator(parse_tree, content).generate_program()

filename_no_extension = filename[:4]

with open("./" + filename_no_extension + ".asm", "w") as f:
    f.write(final_asm)

os.system("nasm -felf64 " + filename_no_extension + ".asm")
os.system("ld " + filename_no_extension + ".o -o " + filename_no_extension)
print("Done!")
