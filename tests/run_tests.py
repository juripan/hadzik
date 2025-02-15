import subprocess as sbp
import os
import time

folders = tuple(filter(lambda x: not x.endswith(".py") , os.listdir("./tests")))
success_count = 0
test_count = len(folders)

def compare_output(output_py: sbp.CompletedProcess[str], output_hdz: sbp.CompletedProcess[str]):
    return output_py.returncode == output_hdz.returncode \
            and output_py.stdout == output_hdz.stdout \
            and output_py.stderr == output_hdz.stderr

for folder in folders:
    out_python = sbp.run(["python3", f"tests/{folder}/{folder}.py"], capture_output=True, text=True)
    
    compilation = sbp.run(["python3", "src/hdz.py", f"tests/{folder}/{folder}.hdz"])
    while not os.path.exists(f"./tests/{folder}/{folder}"): # waits for the compilation to be done so it can run the file
        if compilation.returncode != 0:
            print(f"{"\033[31m"}[FAIL]{"\033[0m"} compilation failed")
            exit(1)
        time.sleep(1)
    
    out_hadzik = sbp.run([f"./tests/{folder}/{folder}"], capture_output=True, text=True)
    
    if compare_output(out_python, out_hadzik):
        print(f"{"\033[92m"}[SUCCESS]{"\033[0m"} \nPython: {out_python} \nHadzik: {out_hadzik}")
        print("---------------------------------------------------------")
        success_count += 1
    else:
        print(f"{"\033[31m"}[FAIL]{"\033[0m"} \nPython: {out_python} \nHadzik: {out_hadzik}")
        print("---------------------------------------------------------")

print(f"End of tests: {success_count} / {test_count}: {success_count / test_count:.0%}")
