"""Entry point:  python main.py --input input.json --output output.json"""
import argparse
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "source"))


def write_json(path, data):
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    rec_id, problem = "", ""
    try:
        with open(args.input, encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, list):  # tolerate a list; use the first item
            raw = raw[0]
        rec_id = str(raw.get("id", ""))
        problem = str(raw.get("problem", ""))
    except Exception as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)

    answer = ""
    try:
        from agent.solver import solve
        from agent import llm
        if problem.strip():
            llm.warmup()
        answer = solve(problem)
    except BaseException as exc:  # output.json must always be valid
        print(f"Agent error: {exc!r}", file=sys.stderr)

    write_json(args.output, {"id": rec_id, "answer": str(answer)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
