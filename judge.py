import os
import subprocess

def run_tests(program, root):

    score = 0
    total = 0
    wrong = []

    for folder in os.listdir(root):

        path = os.path.join(root, folder)

        if not os.path.isdir(path):
            continue

        inp = None
        out = None

        for f in os.listdir(path):

            if f.endswith(".inp"):
                inp = os.path.join(path, f)

            if f.endswith(".out"):
                out = os.path.join(path, f)

        if not inp or not out:
            continue

        total += 1

        temp = os.path.join(path, "temp.out")

        with open(inp) as fin, open(temp, "w") as fout:
            subprocess.run([f"./{program}"], stdin=fin, stdout=fout)

        with open(temp) as a, open(out) as b:

            if a.read().strip() == b.read().strip():
                score += 1
            else:
                wrong.append(folder)

    return score, total, wrong