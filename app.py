import os
import subprocess
import traceback
from flask import Flask, render_template, request

app = Flask(__name__)

UPLOAD = "uploads"
TESTDIR = "tests"

os.makedirs(UPLOAD, exist_ok=True)
os.makedirs(TESTDIR, exist_ok=True)


def run_tests(program, root):

    score = 0
    total = 0
    results = []

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

        try:

            with open(inp) as fin, open(temp, "w") as fout:

                subprocess.run(
                    ["./" + program],
                    stdin=fin,
                    stdout=fout,
                    timeout=2
                )

            with open(temp) as a, open(out) as b:

                if a.read().strip() == b.read().strip():

                    score += 1
                    results.append((folder, "PASS"))

                else:

                    results.append((folder, "WRONG"))

        except subprocess.TimeoutExpired:

            results.append((folder, "TIME LIMIT"))

        except Exception:

            results.append((folder, "ERROR"))

    return score, total, results


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():

    try:

        for root, dirs, files in os.walk(TESTDIR):
            for f in files:
                os.remove(os.path.join(root, f))

        code = request.files["code"]

        code_path = os.path.join(UPLOAD, "main.cpp")
        code.save(code_path)

        compile = subprocess.run(
            ["g++", code_path, "-O2", "-o", "main"],
            capture_output=True,
            text=True
        )

        if compile.returncode != 0:
            return {
                "error": "Compile Error",
                "message": compile.stderr
            }

        subprocess.run(["chmod", "+x", "main"])

        files = request.files.getlist("tests")

        for f in files:

            path = os.path.join(TESTDIR, f.filename)

            os.makedirs(os.path.dirname(path), exist_ok=True)

            f.save(path)

        score, total, results = run_tests("main", TESTDIR)

        return render_template(
            "index.html",
            score=score,
            total=total,
            results=results
        )

    except Exception:

        return {
            "error": traceback.format_exc()
        }


if __name__ == "__main__":
    app.run()
