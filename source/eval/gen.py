"""Generate NEW problems of the 10 families with exact ground truth (fa + en)."""
import itertools
import random

NAMES_FA = ["نیما", "سارا", "رضا", "مینا", "کاوه", "لیلا", "پویا", "نگار", "امیر", "هانیه"]
NAMES_EN = ["Nima", "Sara", "Reza", "Mina", "Kaveh", "Leila", "Pouya", "Negar", "Amir", "Hanieh"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday"]
DAYS_FA = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه"]


def g_algebra(r, lang):
    ids = r.sample(range(10), 3)
    a, b, c = [NAMES_EN[i] for i in ids]
    fa = [NAMES_FA[i] for i in ids]
    x = r.randint(5, 30); k = r.choice([2, 3]); d = r.randint(3, 20)
    vals = {a: k * x, b: x + d, c: x}
    tot = sum(vals.values())
    fmt = f"{a}=<integer>, {b}=<integer>, {c}=<integer>"
    if lang == "fa":
        q = (f"{fa[0]}، {fa[1]} و {fa[2]} در مجموع {tot} سکه دارند. سکه‌های {fa[0]} {k} برابر {fa[2]} است و "
             f"{fa[1]} {d} سکه بیشتر از {fa[2]} دارد. هرکدام چند سکه دارند؟\nپاسخ را دقیقاً با فرمت زیر برگردانید:\n{fmt}")
    else:
        q = (f"{a}, {b} and {c} have {tot} coins in total. {a} has {k} times as many as {c}, and {b} has {d} more than {c}. "
             f"How many does each have?\nReturn the answer exactly in this format:\n{fmt}")
    return q, f"{a}={vals[a]}, {b}={vals[b]}, {c}={vals[c]}"


def g_ordering(r, lang):
    while True:
        items = list("ABCDE"); perm = items[:]; r.shuffle(perm)
        pos = {t: i for i, t in enumerate(perm)}
        cons = []
        x, y = r.sample(items, 2)
        cons.append((f"{x}_before_{y}", lambda p, x=x, y=y: p.index(x) < p.index(y)))
        u, v = r.sample(items, 2)
        cons.append((f"{u}_imm_after_{v}", lambda p, u=u, v=v: p.index(u) == p.index(v) + 1))
        w = r.choice(items)
        cons.append((f"{w}_not_end", lambda p, w=w: p.index(w) not in (0, 4)))
        z = r.choice(items); zi = r.choice([0, 4])
        cons.append((f"{z}_at_{zi}", lambda p, z=z, zi=zi: p.index(z) == zi))
        sols = [p for p in itertools.permutations(items) if all(f(list(p)) for _, f in cons)]
        if len(sols) == 1:
            break
    txt_fa = [f"{x} باید قبل از {y} باشد.", f"{u} باید بلافاصله بعد از {v} باشد.",
              f"{w} نمی‌تواند اولین یا آخرین کار باشد.", f"{z} باید {'اولین' if zi == 0 else 'آخرین'} کار باشد."]
    txt_en = [f"{x} must come before {y}.", f"{u} must come immediately after {v}.",
              f"{w} cannot be the first or last task.", f"{z} must be the {'first' if zi == 0 else 'last'} task."]
    if lang == "fa":
        q = "پنج کار A، B، C، D و E باید دقیقاً یک‌بار در جایگاه‌های ۱ تا ۵ اجرا شوند.\nقیود:\n" + "\n".join("- " + t for t in txt_fa) + \
            "\nاگر فقط یک ترتیب معتبر وجود داشته باشد، کدام کار در جایگاه اول قرار می‌گیرد؟\nفقط حرف آن کار را برگردانید."
    else:
        q = "Five tasks A, B, C, D and E must each run exactly once in positions 1 to 5.\nConstraints:\n" + "\n".join("- " + t for t in txt_en) + \
            "\nIf exactly one valid order exists, which task is first?\nReturn only the letter."
    return q, sols[0][0]


def g_xor(r, lang):
    while True:
        n = 3
        stm = []
        for _ in range(n):
            box = r.randint(1, 3); neg = r.random() < 0.4
            stm.append((box, neg))
        sol = [k for k in (1, 2, 3) if sum(((k == b) != ng) for b, ng in stm) == 1]
        if len(sol) == 1 and len({b for b, _ in stm}) >= 2:
            break
    L = "ABC"
    if lang == "fa":
        lines = [f"{L[i]}: کلید در جعبه {b} {'نیست' if ng else 'است'}." for i, (b, ng) in enumerate(stm)]
        q = "دقیقاً یکی از سه گزاره زیر درست است:\n" + "\n".join(lines) + "\nکلید دقیقاً در یکی از جعبه‌های ۱، ۲ یا ۳ قرار دارد. کلید در کدام جعبه است؟\nفقط یکی از اعداد ۱، ۲ یا ۳ را برگردانید."
    else:
        lines = [f"{L[i]}: The key is {'not ' if ng else ''}in box {b}." for i, (b, ng) in enumerate(stm)]
        q = "Exactly one of the three statements below is true:\n" + "\n".join(lines) + "\nThe key is in exactly one of boxes 1, 2 or 3. Which box?\nReturn only 1, 2 or 3."
    return q, str(sol[0])


def g_schedule(r, lang):
    d1, d2, d3, d4 = r.randint(2, 6), r.randint(3, 8), r.randint(2, 7), r.randint(1, 4)
    ans = max(d1 + d2, d3) + d4
    if lang == "fa":
        q = (f"یک پروژه چهار فعالیت دارد:\n- طراحی {d1} روز زمان می‌برد.\n- پیاده‌سازی {d2} روز زمان می‌برد و فقط پس از پایان طراحی شروع می‌شود.\n"
             f"- بررسی حقوقی {d3} روز زمان می‌برد و همزمان با طراحی آغاز می‌شود.\n- استقرار {d4} روز زمان می‌برد و فقط پس از پایان پیاده‌سازی و بررسی حقوقی شروع می‌شود.\n"
             "روز ۰ شروع پروژه است. زودترین زمان پایان پروژه چند روز پس از شروع است؟\nفقط عدد صحیح را برگردانید.")
    else:
        q = (f"A project has four activities:\n- Design takes {d1} days.\n- Implementation takes {d2} days and can start only after design finishes.\n"
             f"- Legal review takes {d3} days and can start together with design.\n- Deployment takes {d4} days and starts only after both implementation and legal review finish.\n"
             "Day 0 is the project start. What is the earliest finish time in days?\nReturn only the integer.")
    return q, str(ans)


def g_sets(r, lang):
    n = r.randint(30, 80); a = r.randint(12, n - 8); b = r.randint(10, n - 8); both = r.randint(2, min(a, b) - 1)
    if a + b - both > n:
        return g_sets(r, lang)
    ans = n - (a + b - both)
    if lang == "fa":
        q = f"در یک گروه {n} نفره، {a} نفر فوتبال، {b} نفر والیبال و {both} نفر هر دو ورزش را دوست دارند. چند نفر هیچ‌کدام را دوست ندارند؟\nفقط عدد صحیح را برگردانید."
    else:
        q = f"In a group of {n} people, {a} like football, {b} like volleyball and {both} like both. How many like neither?\nReturn only the integer."
    return q, str(ans)


def g_percent(r, lang):
    while True:
        up = r.choice([10, 20, 25, 30, 40, 50]); down = r.choice([10, 20, 25, 30, 40]); base = r.randint(2, 60) * 20
        final = base * (100 + up) * (100 - down) / 10000
        if abs(final - round(final)) < 1e-9:
            break
    if lang == "fa":
        q = f"قیمت کالایی ابتدا {up}٪ افزایش می‌یابد و سپس روی قیمت جدید {down}٪ تخفیف داده می‌شود. مشتری در نهایت {int(round(final))} واحد پرداخت می‌کند. قیمت اولیه چقدر بوده است؟\nفقط عدد صحیح را برگردانید."
    else:
        q = f"A price is first raised by {up}% and then the new price is discounted by {down}%. The customer finally pays {int(round(final))}. What was the original price?\nReturn only the integer."
    return q, str(base)


def g_assign(r, lang):
    people = r.sample(range(10), 4)
    en = [NAMES_EN[i] for i in people]; fa = [NAMES_FA[i] for i in people]
    while True:
        a, b, c, d = range(4)
        cons = []
        def mk():
            kind = r.choice(["before", "fixed", "notday", "after1"])
            p, q = r.sample(range(4), 2)
            if kind == "before": return ("before", p, q)
            if kind == "fixed": return ("fixed", p, r.randrange(4))
            if kind == "notday": return ("not", p, r.randrange(4))
            return ("after1", p, q)
        cons = [mk() for _ in range(4)]
        def ok(perm):  # perm[i] = day index of person i
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
    ans = DAYS[sols[0][t]]
    opts = "\n".join(DAYS)
    if lang == "fa":
        q = f"چهار پژوهشگر {fa[0]}، {fa[1]}، {fa[2]} و {fa[3]} هرکدام در یکی از روزهای دوشنبه تا پنجشنبه ارائه دارند و هیچ دو نفری در یک روز ارائه ندارند.\nقیود:\n" + "\n".join("- " + x for x in fa_t) + f"\n{fa[t]} در چه روزی ارائه می‌دهد؟\nفقط یکی از این چهار عبارت را برگردانید:\n{opts}"
    else:
        q = f"Four researchers {en[0]}, {en[1]}, {en[2]} and {en[3]} each present on one of Monday to Thursday, no two on the same day.\nConstraints:\n" + "\n".join("- " + x for x in en_t) + f"\nOn which day does {en[t]} present?\nReturn only one of these four words:\n{opts}"
    return q, ans


def g_liar(r, lang):
    while True:
        s1 = r.choice(["liar", "truth"]); kind2 = r.choice(["diff", "same", "liar_self"])
        def ok(a, b):  # a,b True=truth-teller
            st1 = (b is False) if s1 == "liar" else (b is True)
            st2 = (a != b) if kind2 == "diff" else (a == b)
            return (a == st1) and (b == st2)
        sols = [(a, b) for a in (True, False) for b in (True, False) if kind2 != "liar_self" and ok(a, b)]
        if len(sols) == 1:
            break
    a, b = sols[0]
    ans = f"Ali={'Truth' if a else 'Lie'}, Bita={'Truth' if b else 'Lie'}"
    opts = "\nAli=Truth, Bita=Truth\nAli=Truth, Bita=Lie\nAli=Lie, Bita=Truth\nAli=Lie, Bita=Lie"
    if lang == "fa":
        s1t = "بیتا دروغگو است" if s1 == "liar" else "بیتا راستگو است"
        s2t = "من و علی از دو نوع متفاوت هستیم" if kind2 == "diff" else "من و علی از یک نوع هستیم"
        q = f"در یک جزیره هر فرد یا همیشه راست می‌گوید یا همیشه دروغ.\nعلی می‌گوید: {s1t}.\nبیتا می‌گوید: {s2t}.\nوضعیت علی و بیتا چیست؟\nدقیقاً یکی از گزینه‌های زیر را برگردانید:{opts}"
    else:
        s1t = "Bita is a liar" if s1 == "liar" else "Bita is a truth-teller"
        s2t = "Ali and I are of different types" if kind2 == "diff" else "Ali and I are of the same type"
        q = f"On an island everyone either always tells the truth or always lies.\nAli says: {s1t}.\nBita says: {s2t}.\nWhat are Ali and Bita?\nReturn exactly one of these options:{opts}"
    return q, ans


def g_path(r, lang):
    from collections import deque
    while True:
        W, H = r.randint(4, 6), r.randint(3, 5)
        blocked = {(r.randrange(W), r.randrange(H)) for _ in range(r.randint(3, 6))}
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
        if t in dist:
            break
    bl = ", ".join(f"({x},{y})" for x, y in sorted(blocked))
    if lang == "fa":
        q = f"یک ربات از ({s[0]},{s[1]}) روی شبکه شروع می‌کند و باید به ({t[0]},{t[1]}) برسد. در هر حرکت دقیقاً یک خانه بالا، پایین، چپ یا راست می‌رود. خانه‌های {bl} مسدود هستند. ربات نمی‌تواند از محدوده 0<=x<={W-1} و 0<=y<={H-1} خارج شود. حداقل چند حرکت لازم است؟\nفقط عدد صحیح را برگردانید."
    else:
        q = f"A robot starts at ({s[0]},{s[1]}) on a grid and must reach ({t[0]},{t[1]}). Each move goes exactly one cell up, down, left or right. Cells {bl} are blocked. It must stay within 0<=x<={W-1} and 0<=y<={H-1}. What is the minimum number of moves?\nReturn only the integer."
    return q, str(dist[t])


def g_digits(r, lang):
    while True:
        S = r.randint(7, 12); pool = r.sample([1, 2, 3, 4, 5, 6], 5); excl = r.choice(pool)
        digs = [d for d in pool if d != excl]
        kind = r.choice(["diff", "mul"])
        sols = []
        for a, b, c in itertools.permutations(digs, 3):
            if a > b and a + b + c == S and ((c == a - b) if kind == "diff" else (c == a * b % 10 or c == a * b)):
                sols.append(f"{a}{b}{c}")
        if len(sols) == 1:
            break
    sset = "{" + ",".join(map(str, sorted(pool))) + "}"
    rel_en = "equals the difference of the first and second digits" if kind == "diff" else "equals the product of the first and second digits"
    rel_fa = "برابر تفاضل رقم اول و دوم است" if kind == "diff" else "برابر حاصل‌ضرب رقم اول و دوم است"
    if lang == "fa":
        q = f"یک کد سه‌رقمی از سه رقم متمایز از مجموعه {sset} ساخته شده است.\nقیود:\n- رقم اول از رقم دوم بزرگ‌تر است.\n- رقم سوم {rel_fa}.\n- مجموع سه رقم برابر {S} است.\n- رقم {excl} استفاده نشده است.\nکد چیست؟\nفقط کد سه‌رقمی را برگردانید."
    else:
        q = f"A three-digit code uses three distinct digits from {sset}.\nConstraints:\n- The first digit is greater than the second.\n- The third digit {rel_en}.\n- The digits sum to {S}.\n- The digit {excl} is not used.\nWhat is the code?\nReturn only the three-digit code."
    return q, sols[0]


FAMILIES = {"algebra": g_algebra, "ordering": g_ordering, "xor_logic": g_xor, "schedule": g_schedule,
            "sets": g_sets, "percent": g_percent, "assignment": g_assign, "liar": g_liar,
            "shortest_path": g_path, "digits": g_digits}


def make_dataset(per_family=6, seed=1):
    r = random.Random(seed)
    data = []
    for fam, fn in FAMILIES.items():
        for i in range(per_family):
            lang = "fa" if i % 2 == 0 else "en"
            q, a = fn(r, lang)
            data.append({"id": f"{fam}-{lang}-{i}", "family": fam, "lang": lang, "problem": q, "expected": a})
    return data
