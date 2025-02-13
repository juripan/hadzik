import sys
import os

from hdzlexer import Tokenizer
from hdzparser import Parser
from hdzgenerator import Generator
from hdzerrors import ErrorHandler

all_flags: tuple[str, ...] = tuple(filter(lambda x: x[0] == "-", sys.argv))
non_flags: tuple[str, ...] = tuple(filter(lambda x: x[0] != "-", sys.argv))[1:]

if "-s" in all_flags:
    ErrorHandler.dialect_errors = True

file_path: str = non_flags[0]

if not file_path.endswith(".hdz"):
    print("File extension is missing or invalid (file extension must be .hdz)")
    exit(1)

with open(file_path, "r") as f:
    content: str = f.read()

tokens = Tokenizer(content).tokenize()
print(tokens)
parse_tree = Parser(tokens, content).parse_program()
# print(parse_tree)
final_asm = Generator(parse_tree, content).generate_program()


if "-n" in all_flags and len(non_flags) > 1:
    filepath_no_extension = non_flags[1]
else:
    filepath_no_extension = file_path.rsplit(".")[0]


with open("./" + filepath_no_extension + ".asm", "w") as f:
    f.write(final_asm)

os.system("nasm -felf64 " + filepath_no_extension + ".asm")
os.system("ld " + filepath_no_extension + ".o -o " + filepath_no_extension)
print("Done!")

if "-r" in all_flags:
    print("Program output".center(80, "-"))
    exit_code = os.system("./" + filepath_no_extension)
    print("-" * 80)
    print(f"Program exited with: {exit_code % 255}") # exit code 1 is 256 for some reason 