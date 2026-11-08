import re

_FA = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_PREFIX = re.compile(
    r"^\s*(final\s*answer|answer|final|result|پاسخ(\s*نهایی)?|جواب)\s*[:：=\-]\s*",
    re.I
)

def _clean(text):
    text = (text or "").translate(_FA)
    text = re.sub(r"```[a-zA-Z]*", "", text).replace("```", "")
    lines = [x.strip() for x in text.strip().splitlines() if x.strip()]
    if not lines:
        return ""
    text = lines[-1]
    for _ in range(2):
        text = _PREFIX.sub("", text)
    text = text.replace("**", "").replace("`", "").strip()
    text = re.sub(r"^\\boxed\{(.*)\}$", r"\1", text).strip()
    if text.startswith("$") and text.endswith("$"):
        text = text.strip("$").strip()
    if not re.search(r"\d\.\d+$", text):
        text = re.sub(r"[.。]\s*$", "", text)
    return re.sub(r"\s+", " ", text).strip()

def _options(problem):
    cue = re.compile(r"یکی از|گزینه|one of|options|choices|following", re.I)
    lines = [x.strip() for x in problem.splitlines()]
    for i, line in enumerate(lines):
        if not cue.search(line):
            continue
        group = []
        for item in lines[i + 1:]:
            item = item.lstrip("-•*").strip()
            if (0 < len(item) <= 40
                and not re.search(r"[\u0600-\u06FF]", item)
                and not re.search(r"[.?:؟]$", item)):
                group.append(item)
            else:
                break
        if len(group) >= 2:
            return group
    return []

def _templates(problem):
    p = problem.translate(_FA)
    for line in p.splitlines():
        if not re.search(r"<\s*integer", line, re.I):
            continue
        m = re.search(r"[A-Za-z_]\w*\s*=\s*<\s*integer", line, re.I)
        if not m:
            continue
        s = line[m.start():]
        s = re.sub(r"<\s*integer\s*>?", "<integer>", s, flags=re.I)
        s = re.sub(r"[^A-Za-z0-9_=<>,; ]", "", s).strip()
        return s
    return None

def _template_regex(template):
    parts = re.split(r"<integer>", template)
    return "^" + r"(-?\d+)".join(re.escape(x) for x in parts) + "$"

def finalize(problem, raw):
    ans = _clean(raw)
    if not ans:
        return ""

    template = _templates(problem)
    if template:
        rx = _template_regex(template)
        if re.fullmatch(rx, ans):
            return ans

        keys = re.findall(r"([A-Za-z_]\w*)\s*=", template)
        pairs = re.findall(r"([A-Za-z_]\w*)\s*[=:]\s*(-?\d+)", ans)
        values = {k.lower(): v for k, v in pairs}
        if keys and all(k.lower() in values for k in keys):
            sep = ", " if ", " in template else "; "
            return sep.join(f"{k}={values[k.lower()]}" for k in keys)
        # Keep invalid answer unchanged; is_valid will reject it.
        return ans

    opts = _options(problem)
    if opts:
        normalized = ans.lower().replace(" ", "").replace(";", ",")
        exact = {x.lower().replace(" ", ""): x for x in opts}
        if normalized in exact:
            return exact[normalized]
        hits = [x for x in opts if x.lower().replace(" ", "") in normalized]
        if len(hits) == 1:
            return hits[0]

    wants_int = re.search(
        r"عدد صحیح|only the integer|single integer|an integer",
        problem, re.I
    )
    if wants_int:
        m = re.fullmatch(r"(-?\d+)\.0+", ans)
        if m:
            return m.group(1)
    return ans

def is_valid(problem, ans):
    if not ans:
        return False

    template = _templates(problem)
    if template:
        return bool(re.fullmatch(_template_regex(template), ans))

    opts = _options(problem)
    if opts:
        return ans in opts

    if re.search(r"عدد صحیح|integer", problem, re.I):
        return bool(re.fullmatch(r"-?\d+", ans))

    # Reject obvious multi-line/explanatory output.
    if "\n" in ans or len(ans) >= 120:
        return False
    return True
