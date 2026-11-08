"""Accuracy evaluation:  python source/eval/run_eval.py --per-family 6 [--dataset file.json]"""
import argparse, json, os, sys, time
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from agent import llm
from agent.solver import solve
from eval.gen import make_dataset
from eval.gen2 import make_dataset as make_dataset2

ap = argparse.ArgumentParser()
ap.add_argument("--per-family", type=int, default=6)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--dataset")
ap.add_argument("--gen2", action="store_true", help="use harder gen2 problem set")
ap.add_argument("--out", default="eval_results.json")
a = ap.parse_args()

data = json.load(open(a.dataset, encoding="utf-8")) if a.dataset else (make_dataset2 if a.gen2 else make_dataset)(a.per_family, a.seed)
calls = {"n": 0}
orig = llm.chat
def counted(*x, **k):
    calls["n"] += 1
    return orig(*x, **k)
llm.chat = counted
import agent.solver as S
S.chat = counted

stats = defaultdict(lambda: [0, 0]); langs = defaultdict(lambda: [0, 0]); rows = []; tt = 0
for d in data:
    c0, t0 = calls["n"], time.time()
    got = solve(d["problem"])
    dt = time.time() - t0; tt += dt
    norm = lambda x: " ".join(str(x).split()).lower()
    accept = d.get("accept") or [d["expected"]]
    ok = norm(got) in {norm(x) for x in accept}
    stats[d["family"]][0] += ok; stats[d["family"]][1] += 1
    langs[d["lang"]][0] += ok; langs[d["lang"]][1] += 1
    rows.append({**d, "got": got, "ok": ok, "secs": round(dt, 1), "llm_calls": calls["n"] - c0})
    print(f"{'OK ' if ok else 'BAD'} {d['id']:<22} exp={d['expected']!r:<28} got={got!r:<28} {dt:.0f}s", flush=True)

tot = sum(v[0] for v in stats.values()); n = sum(v[1] for v in stats.values())
print("\n=== per family ===")
for k, (c, m) in stats.items(): print(f"{k:<14} {c}/{m}  {100*c/m:.0f}%")
print("=== per language ===")
for k, (c, m) in langs.items(): print(f"{k:<4} {c}/{m}  {100*c/m:.0f}%")
print(f"\nTOTAL {tot}/{n} = {100*tot/n:.1f}%   avg calls={calls['n']/n:.2f}   avg time={tt/n:.1f}s")
json.dump(rows, open(a.out, "w"), ensure_ascii=False, indent=1)
