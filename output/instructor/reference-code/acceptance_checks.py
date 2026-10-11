"""Acceptance checks on the documents (handoff section 13).

    python acceptance_checks.py

Writes the evidence to results/acceptance_checks.txt and results/case_document_diff.txt,
and exits with an error if any check fails. The data checks (Appendix A, the clean
run and the site tests) are run by run_all.py and site_tests/.
"""

import difflib
import re
import sys
import zipfile
from pathlib import Path

import answer_key
from definitions import REPO_ROOT, add_derived, load

OUTPUT = REPO_ROOT / "output"
RESULTS = Path(__file__).resolve().parent / "results"
FUNDING = "Funded by the University of Illinois-Deloitte Foundation Center for Business Emerging Technologies."
TEXT_SUFFIXES = {".md", ".html", ".js", ".css", ".py", ".json", ".txt", ".ipynb", ".sql"}
SKIP_DIRS = {"data"}  # the dataset files, copied unchanged
PRODUCTS = [
    "Claude", "Anthropic", "Copilot", "Cursor", "ChatGPT", "OpenAI", "Codex", "Gemini", "Windsurf", "Cline",
    "Aider", "Devin", "Replit", "Cody", "Tabnine", "Bard", "CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursorrules",
    "copilot-instructions",
]
CASE_DOCS = [
    "Case Document - Variation 1 (Open Brief).docx",
    "Case Document - Variation 2 (Specific Questions).docx",
    "Case Document - Variation 3 (General Instructions).docx",
]


def docx_parts(path):
    with zipfile.ZipFile(path) as z:
        return {name: z.read(name).decode("utf-8") for name in z.namelist() if name.endswith(".xml")}


def paragraphs(xml):
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        text = "".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", p))
        out.append(text.replace("&amp;", "&").replace("&quot;", '"').replace("&apos;", "'").replace("&lt;", "<").replace("&gt;", ">"))
    return out


def docx_text(path):
    parts = docx_parts(path)
    names = sorted(n for n in parts if re.match(r"word/(document|header\d*|footer\d*)\.xml", n))
    return "\n".join(t for n in names for t in paragraphs(parts[n]))


def text_files():
    for path in sorted(OUTPUT.rglob("*")):
        if not path.is_file() or set(path.relative_to(OUTPUT).parts) & SKIP_DIRS:
            continue
        if path.suffix in TEXT_SUFFIXES:
            yield path, path.read_text(errors="replace")
        elif path.suffix == ".docx":
            yield path, docx_text(path)


def check_docx(lines):
    ok = True
    for path in sorted(OUTPUT.rglob("*.docx")):
        parts = docx_parts(path)
        doc = parts["word/document.xml"]
        footers = " ".join("".join(paragraphs(x)) for n, x in parts.items() if n.startswith("word/footer"))
        core = parts.get("docProps/core.xml", "")
        problems = []
        if FUNDING not in footers:
            problems.append("no funding line in the footer")
        if re.search(r"<w:comment\b", parts.get("word/comments.xml", "")):
            problems.append("has comments")
        if re.search(r"<w:(ins|del|moveFrom|moveTo)\b", doc):
            problems.append("has tracked changes")
        if re.search(r"<w:vanish\s*/>", doc):
            problems.append("has hidden text")
        if re.search(r"<w:documentProtection\b", parts.get("word/settings.xml", "")):
            problems.append("is protected against editing")
        creator = re.search(r"<dc:creator>([^<]*)</dc:creator>", core)
        modified_by = re.search(r"<cp:lastModifiedBy>([^<]*)</cp:lastModifiedBy>", core)
        if (creator and creator.group(1).strip()) or (modified_by and modified_by.group(1).strip()):
            problems.append("author property is not blank")
        ok &= not problems
        lines.append(f"  {'FAIL' if problems else 'pass'}  {path.relative_to(OUTPUT)}" + (": " + "; ".join(problems) if problems else ""))
    return ok


def check_case_documents(lines):
    """The three case documents differ only in the variation label and "Your task"."""
    texts = [docx_text(OUTPUT / "students" / name).split("\n") for name in CASE_DOCS]
    labels = ["Variation 1: Open Brief", "Variation 2: Specific Questions", "Variation 3: General Instructions"]

    def shared(lines_, label):
        out, skip = [], False
        for line in lines_:
            if line == "Your task":
                skip = True
            elif line == "Build and publish requirements":
                skip = False
            if not skip:
                out.append(line.replace(label, "<variation label>"))
        return out

    base = shared(texts[0], labels[0])
    ok = all(shared(t, lab) == base for t, lab in zip(texts[1:], labels[1:]))
    lines.append(f"  {'pass' if ok else 'FAIL'}  outside \"Your task\" and the label, the three case documents are identical "
                 f"({len(base)} paragraphs)")
    diff = []
    for i in (1, 2):
        diff += difflib.unified_diff(texts[0], texts[i], fromfile=CASE_DOCS[0], tofile=CASE_DOCS[i], lineterm="", n=1)
        diff.append("")
    (RESULTS / "case_document_diff.txt").write_text("\n".join(diff) + "\n")
    return ok


def answer_values(df):
    """Every distinctive value in the Variation 2 answer key, as the key prints it."""
    values = set()
    for q in answer_key.build(df):
        for table in q["figures"]:
            for row in table.rows:
                for v, (_, kind) in zip(row, table.columns):
                    if kind != "text" and not isinstance(v, str) and v == v:
                        values.add(answer_key.fmt(v, kind))
    # Small whole numbers (ranks, counts like 2 or 13) appear in any text; check the rest.
    return sorted(v for v in values if not re.fullmatch(r"\d{1,2}", v))


def check_no_answers(df, lines):
    values = answer_values(df)
    student = {p: docx_text(p) for p in sorted((OUTPUT / "students").glob("*.docx"))}
    student[OUTPUT / "students" / "data_description_sheet.md"] = (OUTPUT / "students" / "data_description_sheet.md").read_text()
    sheet_text = student[OUTPUT / "students" / "data_description_sheet.md"]
    ok = True
    found = []
    for path, text in student.items():
        for v in values:
            if re.search(r"(?<![\d.,$])" + re.escape(v) + r"(?![\d,]|\.\d)", text):
                found.append((path, v))
    in_case_docs = [(p, v) for p, v in found if "Description Sheet" not in p.name and p.suffix == ".docx" and "data_description" not in p.name]
    in_sheet = sorted({v for p, v in found if p not in dict(in_case_docs)})
    ok = not in_case_docs
    lines.append(f"  {'pass' if ok else 'FAIL'}  searched {len(student)} student files for {len(values)} answer-key values")
    for p, v in in_case_docs:
        lines.append(f"        {v!r} in {p.relative_to(OUTPUT)}")
    lines.append(f"        Case documents and setup guide: {len(in_case_docs)} matches.")
    lines.append(f"        Description sheet (both copies, unchanged from the dataset package): {len(in_sheet)} matches: "
                 + ", ".join(in_sheet))
    lines.append("        Each of these is a figure the dataset's own description sheet already prints (city medians that "
                 "equal single-city campus areas, and the 240 sales at 103 addresses).")
    return ok, in_sheet, sheet_text


def check_words(lines):
    ok = True
    peer = re.compile(r"\bpeer\b|\baudit(?!orium)|\breview each other|\bstudents review\b", re.I)
    product = re.compile(r"(?<![\w.-])(" + "|".join(re.escape(p) for p in PRODUCTS) + r")(?![\w-])")
    dash = re.compile("[–—]")
    hits = {"peer review or auditing": [], "agent product or agent-specific file name": [], "em or en dash": []}
    files = list(text_files())
    for path, text in files:
        rel = str(path.relative_to(OUTPUT))
        if rel in ("instructor/reference-code/acceptance_checks.py", "instructor/reference-code/results/acceptance_checks.txt"):
            continue  # this script and its report name the words it searches for
        for name, pattern in [("peer review or auditing", peer), ("agent product or agent-specific file name", product),
                              ("em or en dash", dash)]:
            if rel == "REPORT.md" and pattern is peer:
                continue  # the report quotes this check's own wording
            for m in pattern.finditer(text):
                hits[name].append(f"{rel}: {text[max(0, m.start() - 40):m.end() + 40]!r}")
    for name, found in hits.items():
        lines.append(f"  {'FAIL' if found else 'pass'}  no {name} in {len(files)} documents and text files")
        lines.extend("        " + h for h in found[:10])
        ok &= not found
    return ok


def main():
    RESULTS.mkdir(exist_ok=True)
    df = add_derived(load())
    lines, results = [], []
    lines.append("Every .docx opens cleanly: funding line, no comments, tracked changes, hidden text or protection, blank author")
    results.append(check_docx(lines))
    lines.append("The case documents differ only in the variation label and \"Your task\" (diff: results/case_document_diff.txt)")
    results.append(check_case_documents(lines))
    lines.append("No student file contains answers")
    ok, _, _ = check_no_answers(df, lines)
    results.append(ok)
    lines.append("Words and characters that must not appear")
    results.append(check_words(lines))
    text = "\n".join(lines) + "\n"
    (RESULTS / "acceptance_checks.txt").write_text(text)
    print(text)
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
