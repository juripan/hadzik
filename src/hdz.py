#!/usr/bin/env python3

import sys
import os

from hdzlexer import Tokenizer
from hdzparser import Parser
from hdzgenerator import Generator
from hdzerrors import ErrorHandler


def hdz_help():
    print(
    """Usage:
$ python3 <path to 'hdz.py'> <path to your '.hdz' file> <flags> <custom path if using -n flag>
or using the shebang:
$ <path to 'hdz.py'> <path to your '.hdz' file> <flags> <custom path if using -n flag>
Flags:
--help - displays user manual
-s - switches on the east slovak error messages
-r - after compilation is done runs the compiled file and prints its output
-n - determine a path and name of the compiled file
-d - dumps all of the compiler debug information available to the console""")
    exit(0)


def hdz_run(executable: str):
    print("Program output".center(80, "-"))
    exit_code = os.system("./" + executable)
    print("-" * 80)
    print(f"Program exited with: {exit_code % 255}") # exit code 1 is 256 for some reason


def hdz_to_asm(hdz_src: str) -> list[str]:
    tokens = Tokenizer(hdz_src).tokenize()
    if ErrorHandler.debug_mode:
        print(tokens)
        print("-" * 130)
    parse_tree = Parser(tokens, hdz_src).parse_program()
    if ErrorHandler.debug_mode:
        print(parse_tree)
        print("-" * 130)
    final_asm = Generator(parse_tree, hdz_src).gen_program()
    return final_asm


def asm_to_bin(filepath: str):
    os.system("nasm -felf64 " + filepath + ".asm")
    os.system("ld " + filepath + ".o -o " + filepath)


def main():
    all_flags: tuple[str, ...] = tuple(filter(lambda x: x[0] == "-", sys.argv))
    non_flags: tuple[str, ...] = tuple(filter(lambda x: x[0] != "-", sys.argv))[1:]

    if len(sys.argv) < 2:
        print("Missing arguments run '--help' to show usage", file=sys.stderr)
        exit(1)

    if "--help" in all_flags:
        hdz_help()
    if "-s" in all_flags:
        ErrorHandler.dialect_errors = True
    if "-d" in all_flags:
        ErrorHandler.debug_mode = True

    file_path: str = non_flags[0]
    if not file_path.endswith(".hdz"):
        print("File extension is missing or invalid (file extension must be .hdz)", file=sys.stderr)
        exit(1)

    if "-n" in all_flags and len(non_flags) > 1:
        filepath_no_hdz = non_flags[1]
    else:
        filepath_no_hdz = file_path.rsplit(".")[0] # removes the file extension

    with open(file_path, "r") as f:
        hdz_src: str = f.read()
    
    final_asm = hdz_to_asm(hdz_src)

    with open("./" + filepath_no_hdz + ".asm", "w") as f:
        f.writelines(final_asm)
    
    asm_to_bin(filepath_no_hdz)

    if "-r" in all_flags:
        hdz_run(filepath_no_hdz)

if __name__ == "__main__":
    main()