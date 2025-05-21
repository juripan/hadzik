#!/usr/bin/env python3

# "rec" is passed in as an argument for recording test output

import subprocess as sbp
import os
import sys
import time


def record(folders: tuple[str, ...]):
    for folder in folders:
        output = recompile_and_run(folder)

        assert isinstance(output, str), ValueError(f"ERROR: compilation of {folder} failed")
        with open(f"tests/{folder}/{folder}.txt", "w") as f:
            f.write(output)


def remove(folders: tuple[str, ...]):
    for folder in folders:
        try:
            os.remove(f"tests/{folder}/{folder}.o")
            os.remove(f"tests/{folder}/{folder}.asm")
            os.remove(f"tests/{folder}/{folder}")
        except OSError:
            pass


def recompile_and_run(test_name: str) -> str | sbp.CompletedProcess[str]:
    compilation = sbp.run(["./src/hdzc", f"tests/{test_name}/{test_name}.hdz"], capture_output=True, text=True)
    
    while not os.path.exists(f"./tests/{test_name}/{test_name}"): # waits for the compilation to be done so it can run the file
        if compilation.returncode != 0:
            print(f"{"\033[31m"}[FAIL]{test_name}{"\033[0m"}\nfailed to compile")
            return compilation.stdout
        time.sleep(1)
    out_hadzik = sbp.run([f"./tests/{test_name}/{test_name}"], capture_output=True, text=True)
    out_hadzik_str: str = f"stdout: {out_hadzik.stdout}| stderr: {out_hadzik.stderr}| returncode: {out_hadzik.returncode}"
    return out_hadzik_str


def testing(folders: tuple[str, ...]):
    success_count = 0

    for folder in folders:
        out_hadzik = recompile_and_run(folder)

        with open(f"tests/{folder}/{folder}.txt", "r") as f:
            out_record = f.read()

        if out_record == out_hadzik:
            print(f"{"\033[92m"}[SUCCESS] {folder}{"\033[0m"} \nExpected: {out_record} \nGot: {out_hadzik}")
            success_count += 1
        else:
            print(f"{"\033[31m"}[FAIL] {folder}{"\033[0m"} \nExpected: {out_record} \nGot: {out_hadzik}")
    
    print(f"{success_count} / {len(folders)} Success rate: {success_count/len(folders):.2%}")


def main():
    folders: tuple[str, ...] = tuple(filter(lambda x: not x.endswith(".py"), os.listdir("./tests")))

    if "rec" in sys.argv:
        record(folders)
    elif "clean" in sys.argv:
        remove(folders)
    else:
        testing(folders)

if __name__ == "__main__":
    main()
