from flask import Flask, render_template, request
import os
import subprocess
from judge import run_tests

app = Flask(__name__)

UPLOAD = "uploads"
TESTDIR = "tests"

os.makedirs(UPLOAD, exist_ok=True)
os.makedirs(TESTDIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():

    code = request.files["code"]
    code_path = os.path.join(UPLOAD, "main.cpp")
    code.save(code_path)

    subprocess.run(["g++", code_path, "-O2", "-o", "main"])

    files = request.files.getlist("tests")

    for f in files:
        path = os.path.join(TESTDIR, f.filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        f.save(path)

    score, total, wrong = run_tests("main", TESTDIR)

    return {
        "score": score,
        "total": total,
        "wrong": wrong
    }