import re

CODE_SYSTEM = """You solve reasoning problems (Persian or English) by writing ONE Python 3 program (standard library only).
Rules:
- Compute the answer from the problem; never guess or hardcode. Read EVERY condition literally; do not assume unstated facts.
- Small search space -> enumerate ALL candidates (itertools), keep those satisfying ALL conditions.
- Persian digits are digits (۷=7). Use int/Fraction; never round unless asked.
- Decide uniqueness: exactly one valid solution -> print its answer; none -> print No solution; several valid and the question needs a unique answer (e.g. "if only one ... exists", "the unique ...", "find the code") -> print No unique solution. If all solutions are requested, print them all in the requested format. Counting, probability, sums, minimum/maximum, dates, times and other computed quantities always have ONE answer: compute it and print it; never print No unique solution or No solution for them.
- Print exactly ONE line: only the final answer in the exact requested format (same order, spelling, capitalization, separators; fill templates fully). No labels, no explanation.
- Keep the program SHORT: no comments, no docstrings, no helper text; just the code needed.
- Re-check the result against every condition before printing.
Reply with exactly one ```python code block and nothing else."""

_HINTS = [
    (r"\btruth|\bliar|\blies\b|\balways lie|راستگو|دروغگو|راست می|دروغ می",
     "Truth-teller/liar: enumerate every True/False assignment; a person's type must equal the truth value of their own statement "
     "(truth-teller -> statement true, liar -> statement false). 'different types' means t[a]!=t[b]; 'same type' means t[a]==t[b]."),
    (r"exactly one of|exactly two of|دقیقاً یکی از|دقیقاً دو",
     "Exactly-k-true statements: for each possible location/value, evaluate every statement and count how many are true; keep only values where the count equals k. "
     "A negative statement ('is not in') is true when the value differs."),
    (r"present|ارائه",
     "Day assignment: map Monday..Thursday to 0..3 (or as listed). Enumerate permutations; 'earlier/before' is a strict '<'; 'exactly one day after X' is day[p]==day[X]+1; "
     "'does not present on D' is !=. Print the day name in English exactly as listed."),
    (r"position|جایگاه|immediately|بلافاصله|run exactly once|اجرا شوند|permut",
     "Ordering: enumerate permutations; positions are 1-based when reported. 'A immediately after C' means pos[A]==pos[C]+1; 'B before D' means pos[B]<pos[D]; "
     "'cannot be first or last' means pos not in (1,n). Collect ALL valid orders first, then apply the uniqueness rule."),
    (r"activit|فعالیت|only after|فقط پس از|earliest|زودترین",
     "Scheduling: finish[x]=max(finish of all its prerequisites, 0)+duration[x]; independent activities run in parallel; answer = max finish over all activities."),
    (r"percent|%|٪|درصد|discount|تخفیف|\btax\b|مالیات",
     "Percentages: apply changes sequentially as multipliers with Fraction (e.g. +25% -> 125/100, -20% -> 80/100). For an unknown original price solve original = final / product_of_multipliers exactly."),
    (r"\bboth\b|neither|\bnone\b|هر دو|هیچ‌کدام|هیچکدام|هیچ کدام",
     "Sets: inclusion-exclusion. none = total - |A∪B∪...|, with |A∪B|=|A|+|B|-|A∩B| and the three-set formula including the triple intersection."),
    (r"grid|robot|cell|blocked|مسدود|ربات|شبکه|مختصات",
     "Grid shortest path: BFS from start; neighbors differ by 1 in x or y; stay inside the stated bounds; skip blocked cells; answer = BFS distance to the target."),
    (r"graph|edges|weighted|یال|گراف",
     "Weighted graph: edges are undirected unless stated; use Dijkstra (heapq) and print the shortest distance."),
    (r"digit|رقم|\bcode\b|کد سه|کد چهار|کد چیست",
     "Digits: enumerate the permitted digits with itertools.permutations (distinct digits) and check EVERY condition, including excluded digits, sums and differences; "
     "then apply the uniqueness rule and print the digits concatenated."),
    (r"<integer>|in total|together|مجموع|روی هم|times as many|دو برابر|سه برابر",
     "Algebra: define variables for each person, translate each sentence to an equation, solve by brute force over integers 0..1000 or by exact arithmetic, "
     "and print every variable in the exact template order."),
]


def build_hint(problem):
    p = problem or ""
    hits = []
    for rx, txt in _HINTS:
        if re.search(rx, p, re.I):
            hits.append(txt)
    # keep the most specific ones, bounded to stay short
    return "\n".join("- " + h for h in hits[:2])


COT_SYSTEM = """Solve the problem carefully (Persian or English). Check every condition literally.
If several answers fit and the question needs a unique one, answer No unique solution.
Think briefly, then finish with one line: FINAL: <answer> in the exact requested format (no explanation, no Markdown)."""