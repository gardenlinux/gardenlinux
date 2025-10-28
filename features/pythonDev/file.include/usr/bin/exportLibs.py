#!/bin/python3

import site
import os
import subprocess
import sys
import re
import shutil

# Parses dependencies from ld output
parse_output = re.compile("(?:.*=>)?\\s*(/\\S*).*\n")


# Check for ELF header
def isElf(path: str) -> bool:
    with open(path, "rb") as f:
        return f.read(4) == b"\x7f\x45\x4c\x46"
    

def getInterpreter(path: str) -> str:
    with open(path, "rb") as f:
        head = f.read(19)

        if head[5] == 1:
            arch = head[17:]
        elif head[5] == 2:
            arch = head[17:][::-1]
        else:
            print(f"Error: Unknown endianess value for {path}: expected 1 or 2, but was {head[5]}", file=sys.stderr)
            exit(1)

        if arch == b"\x00\xb7":   # 00b7: aarch64
            return "/lib/ld-linux-aarch64.so.1"
        elif arch == b"\x00\x3e": # 003e: x86_64
            return "/lib64/ld-linux-x86-64.so.2"
        elif arch == b"\x00\x03": # 0003: i686
            return "/lib/ld-linux.so.2"
        else:
            print(f"Error: Unsupported architecture for {path}: only support x86_64 (003e), aarch64 (00b7) and i686 (0003), but was {arch}", file=sys.stderr)
            exit(1)


package_dir = site.getsitepackages()[0]

# Collect ld dependencies for installed pip packages
dependencies = set()
for root, dirs, files in os.walk(package_dir):
    for file in files:
        path = f"{root}/{file}"
        if not os.path.islink(path) and isElf(path):
            out = subprocess.run([getInterpreter(path),"--inhibit-cache", "--list", path], stdout=subprocess.PIPE)
            for dependency in parse_output.findall(out.stdout.decode()):
                dependencies.add(os.path.realpath(dependency))


# Copy dependencies into required_libs folder
if not os.path.isdir("/required_libs"):
    os.mkdir("/required_libs")

for dependency in dependencies:
    os.makedirs(f"/required_libs{os.path.dirname(dependency)}", exist_ok=True)
    shutil.copy2(dependency, f"/required_libs{dependency}")

# Reset timestamps of the parent directories
if len(dependencies) > 0:
    mtime = int(os.stat(dependencies.pop()).st_mtime)
    os.utime("/required_libs", (mtime, mtime))
    for root, dirs, files in os.walk("/required_libs"):
        for dir in dirs:
            os.utime(f"{root}/{dir}", (mtime, mtime))
