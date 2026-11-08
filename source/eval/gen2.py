"""Harder, structurally different 'hidden-like' problems.
Every ground truth is computed by brute force (never by the agent's code).
Usage:  python source/eval/gen2.py --per-family 4 --seed 5 --out /content/hidden_like.json
Items with "ambiguous": true have several valid answers; the grader accepts the
set in "accept" (or the literal "No unique solution")."""
import argparse
import heapq
import itertools
import json
import random

EN = ["Nima", "Sara", "Reza", "Mina", "Kaveh", "Leila", "Pouya", "Negar", "Amir", "Hanieh"]
FA = ["نیما", "سارا", "رضا", "مینا", "کاوه", "لیلا", "پویا", "نگار", "امیر", "هانیه"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday"]
DAYS_FA = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه"]
NO_UNIQUE = "No unique solution"


def L(lang, fa, en):
    return fa if lang == "fa" else en


# ---------------------------------------------------------------- algebra
def g_alg4(r, lang):
    ids = r.sample(range(10), 4)
    en = [EN[i] for i in ids]; fa = [FA[i] for i in ids]
    z = r.randint(4, 15); k = r.choice([2, 3]); d1 = r.randint(2, 12); d2 = r.randint(2, 9)
    v = [k * z, z + d1, z - d2 if z > d2 else z + d2, z]
    sgn = "more" if v[2] > z else "fewer"
    tot = sum(v)
    fmt = ", ".join(f"{n}=<integer>" for n in en)
    q = L(lang,
          f"{fa[0]}، {fa[1]}، {fa[2]} و {fa[3]} روی هم {tot} مداد دارند. {fa[0]} {k} برابر {fa[3]} مداد دارد، "
          f"{fa[1]} {d1} مداد بیشتر از {fa[3]} دارد و {fa[2]} {abs(v[2]-z)} مداد {'بیشتر' if v[2] > z else 'کمتر'} از {fa[3]} دارد. "
          f"هرکدام چند مداد دارند؟\nپاسخ را دقیقاً با فرمت زیر برگردانید:\n{fmt}",
          f"{en[0]}, {en[1]}, {en[2]} and {en[3]} have {tot} pencils together. {en[0]} has {k} times as many as {en[3]}, "
          f"{en[1]} has {d1} more than {en[3]}, and {en[2]} has {abs(v[2]-z)} {sgn} than {en[3]}. "
          f"How many does each have?\nReturn exactly this format:\n{fmt}")
    return q, ", ".join(f"{n}={x}" for n, x in zip(en, v))


def g_alg_lin(r, lang):
    x = r.randint(3, 40); a = r.randint(2, 9); b = r.randint(2, 30)
    v = a * x + b
    q = L(lang, f"عددی را در {a} ضرب می‌کنیم و سپس {b} واحد به آن اضافه می‌کنیم؛ حاصل {v} می‌شود. آن عدد چند است؟\nفقط عدد صحیح را برگردانید.",
          f"A number is multiplied by {a} and then increased by {b}. The result is {v}. What is the number?\nReturn only the integer.")
    return q, str(x)


# ---------------------------------------------------------------- ordering
def _order_sols(items, cons):
    return [p for p in itertools.permutations(items) if all(f(list(p)) for f in cons)]


def _order_cons(r, items, n):
    cons, tx_fa, tx_en = [], [], []
    for _ in range(n):
        k = r.choice(["before", "imm", "notend", "fixed"])
        x, y = r.sample(items, 2)
        if k == "before":
            cons.append(lambda p, x=x, y=y: p.index(x) < p.index(y))
            tx_fa.append(f"{x} باید قبل از {y} باشد."); tx_en.append(f"{x} must come before {y}.")
        elif k == "imm":
            cons.append(lambda p, x=x, y=y: p.index(x) == p.index(y) + 1)
            tx_fa.append(f"{x} باید بلافاصله بعد از {y} باشد."); tx_en.append(f"{x} must come immediately after {y}.")
        elif k == "notend":
            cons.append(lambda p, x=x: p.index(x) not in (0, len(p) - 1))
            tx_fa.append(f"{x} نمی‌تواند اولین یا آخرین کار باشد."); tx_en.append(f"{x} cannot be the first or last task.")
        else:
            pos = r.choice([0, len(items) - 1])
            cons.append(lambda p, x=x, pos=pos: p.index(x) == pos)
            tx_fa.append(f"{x} باید {'اولین' if pos == 0 else 'آخرین'} کار باشد."); tx_en.append(f"{x} must be the {'first' if pos == 0 else 'last'} task.")
    return cons, tx_fa, tx_en


def g_order_full(r, lang):
    items = list("ABCDE")
    while True:
        cons, tf, te = _order_cons(r, items, 5)
        sols = _order_sols(items, cons)
        if len(sols) == 1:
            break
    q = L(lang, "پنج کار A تا E باید دقیقاً یک‌بار اجرا شوند.\nقیود:\n" + "\n".join("- " + t for t in tf) +
          "\nترتیب کامل اجرا را (با ویرگول و بدون فاصله، مثل A,B,C,D,E) برگردانید.",
          "Five tasks A to E must each run exactly once.\nConstraints:\n" + "\n".join("- " + t for t in te) +
          "\nReturn the complete order separated by commas with no spaces (e.g. A,B,C,D,E).")
    return q, ",".join(sols[0])


def g_order_pos(r, lang):
    items = list("ABCDE")
    while True:
        cons, tf, te = _order_cons(r, items, 4)
        sols = _order_sols(items, cons)
        if len(sols) == 1:
            break
    pos = r.randint(1, 5); letter = r.choice(items)
    q = L(lang, "پنج کار A، B، C، D و E باید دقیقاً یک‌بار در جایگاه‌های ۱ تا ۵ اجرا شوند.\nقیود:\n" + "\n".join("- " + t for t in tf) +
          f"\nکار {letter} در کدام جایگاه قرار دارد؟\nفقط عدد جایگاه را برگردانید.",
          "Five tasks A, B, C, D and E must each run exactly once in positions 1 to 5.\nConstraints:\n" + "\n".join("- " + t for t in te) +
          f"\nIn which position is task {letter}?\nReturn only the position number.")
    return q, str(sols[0].index(letter) + 1)


def g_order_ambig(r, lang):
    items = list("ABCDE")
    while True:
        cons, tf, te = _order_cons(r, items, 3)
        sols = _order_sols(items, cons)
        firsts = {s[0] for s in sols}
        if len(sols) >= 2 and len(firsts) >= 2:
            break
    q = L(lang, "پنج کار A، B، C، D و E باید دقیقاً یک‌بار در جایگاه‌های ۱ تا ۵ اجرا شوند.\nقیود:\n" + "\n".join("- " + t for t in tf) +
          "\nاگر فقط یک ترتیب معتبر وجود داشته باشد، کدام کار در جایگاه اول قرار می‌گیرد؟\nفقط حرف آن کار را برگردانید.",
          "Five tasks A, B, C, D and E must each run exactly once in positions 1 to 5.\nConstraints:\n" + "\n".join("- " + t for t in te) +
          "\nIf only one valid order exists, which task is first?\nReturn only the letter.")
    return q, NO_UNIQUE, {"ambiguous": True, "accept": sorted(firsts) + [NO_UNIQUE]}


# ---------------------------------------------------------------- logic puzzles
def g_xor4(r, lang):
    while True:
        stm = [(r.randint(1, 4), r.random() < 0.4) for _ in range(4)]
        sol = [k for k in (1, 2, 3, 4) if sum(((k == b) != ng) for b, ng in stm) == 2]
        if len(sol) == 1 and len({b for b, _ in stm}) >= 3:
            break
    Ls = "ABCD"
    q = L(lang, "دقیقاً دو گزاره از چهار گزاره زیر درست است:\n" +
          "\n".join(f"{Ls[i]}: گنج در اتاق {b} {'نیست' if ng else 'است'}." for i, (b, ng) in enumerate(stm)) +
          "\nگنج دقیقاً در یکی از اتاق‌های ۱ تا ۴ است. در کدام اتاق است؟\nفقط یک عدد برگردانید.",
          "Exactly two of the four statements below are true:\n" +
          "\n".join(f"{Ls[i]}: The treasure is {'not ' if ng else ''}in room {b}." for i, (b, ng) in enumerate(stm)) +
          "\nThe treasure is in exactly one of rooms 1 to 4. Which room?\nReturn only a number.")
    return q, str(sol[0])


def g_liar3(r, lang):
    nm = ["A", "B", "C"]
    while True:
        st = []
        for i in range(3):
            kind = r.choice(["liar", "truth", "diff", "same"])
            others = [x for x in range(3) if x != i]
            st.append((kind, r.choice(others) if kind in ("liar", "truth") else tuple(others)))
        sols = []
        for t in itertools.product([True, False], repeat=3):
            ok = True
            for i, (kind, tg) in enumerate(st):
                if kind == "liar": said = not t[tg]
                elif kind == "truth": said = t[tg]
                elif kind == "diff": said = t[tg[0]] != t[tg[1]]
                else: said = t[tg[0]] == t[tg[1]]
                if t[i] != said:
                    ok = False
            if ok:
                sols.append(t)
        if len(sols) == 1:
            break
    def en_s(i, kind, tg):
        if kind == "liar": return f"{nm[i]} says: {nm[tg]} is a liar."
        if kind == "truth": return f"{nm[i]} says: {nm[tg]} is truthful."
        if kind == "diff": return f"{nm[i]} says: {nm[tg[0]]} and {nm[tg[1]]} are of different types."
        return f"{nm[i]} says: {nm[tg[0]]} and {nm[tg[1]]} are of the same type."
    def fa_s(i, kind, tg):
        if kind == "liar": return f"{nm[i]} می‌گوید: {nm[tg]} دروغگو است."
        if kind == "truth": return f"{nm[i]} می‌گوید: {nm[tg]} راستگو است."
        if kind == "diff": return f"{nm[i]} می‌گوید: {nm[tg[0]]} و {nm[tg[1]]} از دو نوع متفاوت‌اند."
        return f"{nm[i]} می‌گوید: {nm[tg[0]]} و {nm[tg[1]]} از یک نوع‌اند."
    q = L(lang, "سه نفر A، B و C هر کدام یا همیشه راست می‌گویند یا همیشه دروغ.\n" + "\n".join(fa_s(i, *st[i]) for i in range(3)) +
          "\nنوع هر سه نفر را مشخص کنید.\nدقیقاً با این فرمت برگردانید: A=Truth, B=Lie, C=Truth (Truth یا Lie برای هر نفر)",
          "Three people A, B and C each either always tell the truth or always lie.\n" + "\n".join(en_s(i, *st[i]) for i in range(3)) +
          "\nDetermine each person's type.\nReturn exactly in this format: A=Truth, B=Lie, C=Truth (Truth or Lie for each person)")
    t = sols[0]
    return q, ", ".join(f"{nm[i]}={'Truth' if t[i] else 'Lie'}" for i in range(3))


# ---------------------------------------------------------------- scheduling
def g_dag(r, lang):
    n = 5
    names = list("ABCDE")
    dur = {x: r.randint(1, 7) for x in names}
    deps = {x: [] for x in names}
    for i in range(1, n):
        for j in range(i):
            if r.random() < 0.4:
                deps[names[i]].append(names[j])
        if not deps[names[i]] and r.random() < 0.6:
            deps[names[i]].append(names[r.randrange(i)])
    fin = {}
    for x in names:
        fin[x] = max([fin[d] for d in deps[x]], default=0) + dur[x]
    ans = max(fin.values())
    lf = [f"- {x} {dur[x]} روز طول می‌کشد" + (f" و فقط پس از پایان {' و '.join(deps[x])} شروع می‌شود." if deps[x] else " و می‌تواند از روز ۰ شروع شود.") for x in names]
    le = [f"- {x} takes {dur[x]} days" + (f" and can start only after {' and '.join(deps[x])} finish{'es' if len(deps[x])==1 else ''}." if deps[x] else " and can start at day 0.") for x in names]
    q = L(lang, "یک پروژه پنج فعالیت دارد:\n" + "\n".join(lf) + "\nفعالیت‌های مستقل می‌توانند همزمان انجام شوند. زودترین زمان پایان پروژه چند روز است؟\nفقط عدد صحیح را برگردانید.",
          "A project has five activities:\n" + "\n".join(le) + "\nIndependent activities may run in parallel. What is the earliest project finish time in days?\nReturn only the integer.")
    return q, str(ans)


# ---------------------------------------------------------------- sets / percent
def g_sets3(r, lang):
    while True:
        a, b, c = r.randint(15, 30), r.randint(15, 30), r.randint(15, 30)
        ab, ac, bc = r.randint(3, 9), r.randint(3, 9), r.randint(3, 9)
        abc = r.randint(1, 3)
        union = a + b + c - ab - ac - bc + abc
        n = union + r.randint(2, 12)
        if min(ab, ac, bc) > abc and ab <= min(a, b) and ac <= min(a, c) and bc <= min(b, c):
            break
    q = L(lang, f"در یک مدرسه {n} دانش‌آموز هست. {a} نفر فوتبال، {b} نفر والیبال و {c} نفر شنا دارند. {ab} نفر فوتبال و والیبال، {ac} نفر فوتبال و شنا، {bc} نفر والیبال و شنا و {abc} نفر هر سه را دارند. چند نفر هیچ‌کدام را ندارند؟\nفقط عدد صحیح را برگردانید.",
          f"A school has {n} students. {a} play football, {b} volleyball and {c} swimming. {ab} do football and volleyball, {ac} football and swimming, {bc} volleyball and swimming, and {abc} do all three. How many do none?\nReturn only the integer.")
    return q, str(n - union)


def g_percent3(r, lang):
    while True:
        base = r.randint(2, 50) * 20
        u = r.choice([10, 20, 25, 50]); d = r.choice([10, 20, 25, 30]); tx = r.choice([5, 10, 20])
        final = base * (100 + u) * (100 - d) * (100 + tx) / 1_000_000
        if abs(final - round(final)) < 1e-9:
            break
    q = L(lang, f"قیمت کالایی ابتدا {u}٪ افزایش می‌یابد، سپس {d}٪ تخفیف می‌خورد و در پایان {tx}٪ مالیات به قیمت اضافه می‌شود. قیمت نهایی {int(round(final))} است. قیمت اولیه چند بوده است؟\nفقط عدد صحیح را برگردانید.",
          f"A price is first raised by {u}%, then discounted by {d}%, and finally {tx}% tax is added. The final price is {int(round(final))}. What was the original price?\nReturn only the integer.")
    return q, str(base)


# ---------------------------------------------------------------- graph / grid / digits
def g_dijkstra(r, lang):
    while True:
        nodes = list("ABCDEF")
        edges = {}
        for i, x in enumerate(nodes):
            for y in nodes[i + 1:]:
                if r.random() < 0.5:
                    edges[(x, y)] = r.randint(1, 9)
        dist = {n: 10**9 for n in nodes}; dist["A"] = 0; pq = [(0, "A")]
        while pq:
            dd, u = heapq.heappop(pq)
            if dd > dist[u]:
                continue
            for (x, y), w in edges.items():
                for p, qn in ((x, y), (y, x)):
                    if p == u and dd + w < dist[qn]:
                        dist[qn] = dd + w; heapq.heappush(pq, (dist[qn], qn))
        if dist["F"] < 10**9 and len(edges) >= 7:
            break
    es = "، ".join(f"{x}-{y}={w}" for (x, y), w in edges.items())
    ee = ", ".join(f"{x}-{y}={w}" for (x, y), w in edges.items())
    q = L(lang, f"یک گراف بدون جهت با یال‌های وزن‌دار زیر داریم: {es}. کوتاه‌ترین فاصله از A به F چند است؟\nفقط عدد صحیح را برگردانید.",
          f"An undirected weighted graph has edges: {ee}. What is the shortest distance from A to F?\nReturn only the integer.")
    return q, str(dist["F"])


def g_grid(r, lang):
    from collections import deque
    while True:
        W, H = r.randint(5, 7), r.randint(4, 6)
        blocked = {(r.randrange(W), r.randrange(H)) for _ in range(r.randint(5, 10))}
        s, t = (0, 0), (W - 1, H - 1)
        if s in blocked or t in blocked:
            continue
        dist = {s: 0}; dq = deque([s])
        while dq:
            x, y = dq.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in blocked and n not in dist:
                    dist[n] = dist[(x, y)] + 1; dq.append(n)
        if t in dist and dist[t] > (W - 1 + H - 1):
            break
    bl = ", ".join(f"({x},{y})" for x, y in sorted(blocked))
    q = L(lang, f"یک ربات از (0,0) شروع می‌کند و باید به ({t[0]},{t[1]}) برسد. هر حرکت دقیقاً یک خانه بالا، پایین، چپ یا راست است. خانه‌های {bl} مسدودند. ربات باید در محدوده 0<=x<={W-1} و 0<=y<={H-1} بماند. حداقل تعداد حرکت چند است؟\nفقط عدد صحیح را برگردانید.",
          f"A robot starts at (0,0) and must reach ({t[0]},{t[1]}). Each move is one cell up, down, left or right. Cells {bl} are blocked. It must stay in 0<=x<={W-1} and 0<=y<={H-1}. What is the minimum number of moves?\nReturn only the integer.")
    return q, str(dist[t])


def g_digits_par(r, lang):
    while True:
        S = r.randint(9, 17)
        pa, pb = r.choice(["even", "odd"]), r.choice(["even", "odd"])
        rel = r.choice(["a>b", "a<b"])
        sols = []
        for a_, b_, c_ in itertools.permutations(range(1, 8), 3):
            if (a_ + b_ + c_ == S and (a_ % 2 == 0) == (pa == "even") and (b_ % 2 == 0) == (pb == "even")
                    and ((a_ > b_) if rel == "a>b" else (a_ < b_)) and c_ > 2):
                sols.append(f"{a_}{b_}{c_}")
        if len(sols) == 1:
            break
    pf = {"even": "زوج", "odd": "فرد"}
    rf = "رقم اول از رقم دوم بزرگ‌تر است" if rel == "a>b" else "رقم اول از رقم دوم کوچک‌تر است"
    re_ = "The first digit is greater than the second" if rel == "a>b" else "The first digit is smaller than the second"
    q = L(lang, f"یک عدد سه‌رقمی با رقم‌های متمایز از ۱ تا ۷ داریم. رقم اول {pf[pa]} است، رقم دوم {pf[pb]} است، {rf}، رقم سوم بزرگ‌تر از ۲ است و مجموع رقم‌ها {S} است. عدد چند است؟\nفقط عدد را برگردانید.",
          f"A three-digit number has distinct digits from 1 to 7. The first digit is {pa}, the second digit is {pb}. {re_}. The third digit is greater than 2 and the digits sum to {S}. What is the number?\nReturn only the number.")
    return q, sols[0]


def g_digits_amb(r, lang):
    """Like public problem 10: several codes fit -> ambiguous."""
    while True:
        S = r.randint(7, 12)
        sols = [f"{a}{b}{c}" for a, b, c in itertools.permutations([1, 2, 3, 4, 5], 3)
                if a > b and c == a - b and a + b + c == S]
        if len(sols) >= 2:
            break
    q = L(lang, f"یک کد سه‌رقمی از سه رقم متمایز از مجموعه {{1,2,3,4,5}} ساخته شده است.\nقیود:\n- رقم اول از رقم دوم بزرگ‌تر است.\n- رقم سوم برابر تفاضل رقم اول و دوم است.\n- مجموع سه رقم برابر {S} است.\nکد چیست؟\nفقط کد سه‌رقمی را برگردانید.",
          f"A three-digit code uses three distinct digits from {{1,2,3,4,5}}.\nConstraints:\n- The first digit is greater than the second.\n- The third digit equals the first minus the second.\n- The digits sum to {S}.\nWhat is the code?\nReturn only the three-digit code.")
    return q, NO_UNIQUE, {"ambiguous": True, "accept": sols + [NO_UNIQUE]}


def g_assign4(r, lang):
    people = r.sample(range(10), 4)
    en = [EN[i] for i in people]; fa = [FA[i] for i in people]
    while True:
        cons = []
        for _ in range(4):
            k = r.choice(["before", "fixed", "not", "after1"])
            p, q = r.sample(range(4), 2)
            cons.append((k, p, q if k in ("before", "after1") else r.randrange(4)))
        def ok(perm):
            for k, p, q in cons:
                if k == "before" and not perm[p] < perm[q]: return False
                if k == "fixed" and perm[p] != q: return False
                if k == "not" and perm[p] == q: return False
                if k == "after1" and perm[p] != perm[q] + 1: return False
            return True
        sols = [p for p in itertools.permutations(range(4)) if ok(p)]
        if len(sols) == 1:
            break
    t = r.randrange(4)
    en_t, fa_t = [], []
    for k, p, q in cons:
        if k == "before": en_t.append(f"{en[p]} presents earlier than {en[q]}."); fa_t.append(f"{fa[p]} زودتر از {fa[q]} ارائه می‌دهد.")
        if k == "fixed": en_t.append(f"{en[p]} presents on {DAYS[q]}."); fa_t.append(f"{fa[p]} {DAYS_FA[q]} ارائه می‌دهد.")
        if k == "not": en_t.append(f"{en[p]} does not present on {DAYS[q]}."); fa_t.append(f"{fa[p]} {DAYS_FA[q]} ارائه نمی‌دهد.")
        if k == "after1": en_t.append(f"{en[p]} presents exactly one day after {en[q]}."); fa_t.append(f"{fa[p]} دقیقاً یک روز بعد از {fa[q]} ارائه می‌دهد.")
    fmt = ", ".join(f"{en[i]}=Day" for i in range(4))
    ans = ", ".join(f"{en[i]}={DAYS[sols[0][i]]}" for i in range(4))
    q = L(lang, f"چهار نفر {fa[0]}، {fa[1]}، {fa[2]} و {fa[3]} هرکدام در یکی از روزهای دوشنبه تا پنجشنبه ارائه دارند و هیچ دو نفری هم‌روز نیستند.\nقیود:\n" + "\n".join("- " + x for x in fa_t) +
          f"\nبرنامه‌ی کامل را دقیقاً با این فرمت برگردانید (نام لاتین و نام روز انگلیسی):\n{fmt}",
          f"Four people {en[0]}, {en[1]}, {en[2]} and {en[3]} each present on one of Monday to Thursday, no two on the same day.\nConstraints:\n" + "\n".join("- " + x for x in en_t) +
          f"\nReturn the full schedule exactly in this format:\n{fmt}")
    return q, ans


FAMILIES = {
    "alg4": g_alg4, "alg_lin": g_alg_lin,
    "order_full": g_order_full, "order_pos": g_order_pos, "order_ambig": g_order_ambig,
    "xor4": g_xor4, "liar3": g_liar3, "dag": g_dag, "sets3": g_sets3, "percent3": g_percent3,
    "dijkstra": g_dijkstra, "grid": g_grid, "digits_par": g_digits_par, "digits_amb": g_digits_amb,
    "assign4": g_assign4,
}


def make_dataset(per_family=4, seed=1):
    r = random.Random(seed)
    data = []
    for fam, fn in FAMILIES.items():
        for i in range(per_family):
            lang = "fa" if i % 2 == 0 else "en"
            res = fn(r, lang)
            q, a = res[0], res[1]
            item = {"id": f"{fam}-{lang}-{i}", "family": fam, "lang": lang, "problem": q, "expected": a}
            if len(res) > 2:
                item.update(res[2])
            data.append(item)
    return data


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-family", type=int, default=4)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default="hidden_like.json")
    a = ap.parse_args()
    ds = make_dataset(a.per_family, a.seed)
    json.dump(ds, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {len(ds)} problems to {a.out}")
