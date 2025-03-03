# "rec" is passed in as an argument for recording test output
import subprocess as sbp
import os
import sys
import time

success_count = 0

def testing(folder: str, out_hadzik: str):
    global success_count
    with open(f"tests/{folder}/{folder}.txt", "r") as f:
        out_record = f.read()

    if out_record == out_hadzik:
        print(f"{"\033[92m"}[SUCCESS]{"\033[0m"} \nExpected: {out_record} \nGot: {out_hadzik}")
        success_count += 1
    else:
        print(f"{"\033[31m"}[FAIL]{"\033[0m"} \nExpected: {out_record} \nGot: {out_hadzik}")


def record(name: str, output: str):
    with open(f"tests/{name}/{name}.txt", "w") as f:
        f.write(output)


def main():
    folders = tuple(filter(lambda x: not x.endswith(".py"), os.listdir("./tests")))

    for folder in folders:
        compilation = sbp.run(["python3", "src/hdz.py", f"tests/{folder}/{folder}.hdz"])
        
        while not os.path.exists(f"./tests/{folder}/{folder}"): # waits for the compilation to be done so it can run the file
            if compilation.returncode != 0:
                print(f"{"\033[31m"}[FAIL]{"\033[0m"} compilation failed")
                exit(1)
            time.sleep(1)
        
        out_hadzik = sbp.run([f"./tests/{folder}/{folder}"], capture_output=True, text=True)
        out_hadzik_str: str = f"stdout: {out_hadzik.stdout}| stderr: {out_hadzik.stderr}| returncode: {out_hadzik.returncode}"
        
        if "rec" in sys.argv:
            record(folder, out_hadzik_str)
        else:
            testing(folder, out_hadzik_str)
    
    if "rec" not in sys.argv:
        print(f"{success_count} / {len(folders)} Success rate: {success_count/len(folders):.2%}")

if __name__ == "__main__":
    main()
