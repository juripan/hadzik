#!/usr/bin/env python3

import subprocess as sbp
import os
import sys
import time

def rename(folder: list[str], new_folder_name: str):
    folder_path = "/".join(folder[:-1])
    folder_name = folder[-1]
    
    try:
        os.rename(f"./tests/{folder_path}/{folder_name}",
                f"./tests/{folder_path}/{new_folder_name}")
        os.rename(f"./tests/{folder_path}/{new_folder_name}/{folder_name}.hdz", 
                f"./tests/{folder_path}/{new_folder_name}/{new_folder_name}.hdz")
        os.rename(f"./tests/{folder_path}/{new_folder_name}/{folder_name}.expected", 
                f"./tests/{folder_path}/{new_folder_name}/{new_folder_name}.expected")
    except OSError as error:
        print(error)

def record(folders: tuple[str, ...], subfolder: str = ""):
    for folder in folders:
        if folder == "_errors":
            err_folders: tuple[str, ...] = tuple(filter(lambda x: not x.endswith(".py"), os.listdir(f"./tests/{folder}")))
            record(err_folders, folder)
            continue

        output = recompile_and_run(folder, subfolder)

        with open(f"tests/{subfolder}/{folder}/{folder}.expected", "w") as f:
            f.write(output)


def remove(folders: tuple[str, ...], subfolder: str = ""):
    for folder in folders:
        if folder == "_errors":
            continue

        rem = filter(lambda x: not x.endswith((".hdz", ".expected")), os.listdir(f"./tests/{subfolder}/{folder}"))
        
        for file in rem:
            try:
                os.remove(f"tests/{subfolder}/{folder}/{file}")
            except OSError as e:
                print(e)

def recompile_and_run(test_name: str, subfolder: str="") -> str:
    compilation = sbp.run(["./src/hdzc", f"tests/{subfolder}/{test_name}/{test_name}.hdz", "-c"], capture_output=True, text=True)
    
    while not os.path.exists(f"./tests/{subfolder}/{test_name}/{test_name}"): # waits for the compilation to be done so it can run the file
        if compilation.returncode != 0:
            if not subfolder:
                print(f"[INFO] {test_name} failed to compile")
            return compilation.stdout
        time.sleep(1)
    out_hadzik = sbp.run([f"./tests/{subfolder}/{test_name}/{test_name}"], capture_output=True, text=True)
    out_hadzik_str: str = f"stdout: {out_hadzik.stdout}| stderr: {out_hadzik.stderr}| returncode: {out_hadzik.returncode}"
    return out_hadzik_str


def testing(folders: tuple[str, ...], subfolder: str = ""):
    success_count = 0
    folder_count = len(folders)

    for folder in folders:
        if folder == "_errors":
            err_folders: tuple[str, ...] = tuple(filter(lambda x: not x.endswith(".py"), os.listdir(f"./tests/{folder}")))
            testing(err_folders, folder)
            folder_count -= 1
            continue

        out_hadzik = recompile_and_run(folder, subfolder)

        with open(f"tests/{subfolder}/{folder}/{folder}.expected", "r") as f:
            out_record = f.read()

        if out_record == out_hadzik:
            print(f"{"\033[92m"}[SUCCESS] {"\033[0m"}{folder}")
            success_count += 1
        else:
            print(f"{"\033[31m"}[FAIL] {folder}{"\033[0m"} \nExpected: {out_record} \nGot: {out_hadzik}")
    
    assert folder_count > 0, f"{folders}"
    print(f"{subfolder} {success_count} / {folder_count} Success rate: {success_count/folder_count:.2%}")


def main():
    folders: tuple[str, ...] = tuple(filter(lambda x: not x.endswith(".py"), os.listdir("./tests")))

    if "rec" in sys.argv:
        print("Recording new results...")
        record(folders)
        print("Recording finished!")
    elif "clr" in sys.argv:
        print("Removing generated files...")
        remove(folders)
        print("Cleaning finished!")
    elif "ren" in sys.argv:
        if len(sys.argv) < 4:
            print("ERROR: invalid argument count")
            exit(1)
        rename(sys.argv[2].split("/"), sys.argv[3])
    elif len(sys.argv) == 1:
        testing(folders)
    else:
        print("Incorrect usage!")
        print("Usage: $ ./run_tests.py [rec | clr]")
        exit(1)

if __name__ == "__main__":
    main()
