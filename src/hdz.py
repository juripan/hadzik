import sys
import os

from hdzlexer import Tokenizer
from hdzparser import Parser
from hdzgenerator import Generator
from hdzerrors import ErrorHandler

all_flags: list[str] = list(filter(lambda x: x[0] == "-", sys.argv))

if "-s" in all_flags:
    ErrorHandler.dialect_errors = True

filename: str = sys.argv[1]

if not filename.endswith(".hdz"):
    print("CompilerError: file extension is missing or invalid (file extension must be .hdz and file must be the first arg)")
    exit(1)

with open("./" + filename, "r") as f:
    content: str = f.read()

tokens = Tokenizer(content).tokenize()
print(tokens)
parse_tree = Parser(tokens, content).parse_program()
print(parse_tree)
final_asm = Generator(parse_tree, content).generate_program()

filepath_no_extension = filename.split(".")[0]

with open("./" + filepath_no_extension + ".asm", "w") as f:
    f.write(final_asm)

os.system("nasm -felf64 " + filepath_no_extension + ".asm")
os.system("ld " + filepath_no_extension + ".o -o " + filepath_no_extension)
print("Done!")
