#!/usr/bin/env python3
"""Check whether a repository has a README, installation instructions, usage examples, a license file and contribution guidance."""

import argparse
import json
import re
from pathlib import Path


def inspect(folder):
    if not folder.is_dir():
        raise ValueError("Repository folder does not exist")
    files = {p.name.lower(): p for p in folder.iterdir() if p.is_file()}
    readme = next((files[n] for n in ("readme.md", "readme.markdown", "readme.rst", "readme.txt", "readme") if n in files), None)
    text = readme.read_text(encoding="utf-8") if readme else ""
    checks = {
        "readme_present": readme is not None,
        "installation_guidance": bool(re.search(r"\b(install(?:ation)?|setup|getting started)\b", text, re.I)),
        "usage_guidance": bool(re.search(r"\b(usage|examples?|quick ?start)\b", text, re.I)),
        "license_file": any(re.fullmatch(r"(?:licen[cs]e|copying)(?:\..+)?", n) for n in files),
        "contribution_guidance": any(n.startswith("contributing") for n in files) or (folder / ".github" / "CONTRIBUTING.md").is_file() or bool(re.search(r"\bcontribut(?:e|ing|ions?)\b", text, re.I)),
    }
    advice = {
        "readme_present": "Add a README explaining the problem and current project status.",
        "installation_guidance": "Document requirements and installation steps.",
        "usage_guidance": "Include a runnable usage example.",
        "license_file": "Choose an appropriate license and include its full text.",
        "contribution_guidance": "Explain how to report issues and propose changes.",
    }
    return {"checks": checks, "passed": sum(checks.values()), "total": len(checks), "suggestions": [advice[k] for k, ok in checks.items() if not ok]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("folder", type=Path)
    a = p.parse_args()
    try:
        report = inspect(a.folder)
    except (OSError, UnicodeError, ValueError) as exc:
        p.exit(2, f"Input error: {exc}\n")
    print(json.dumps(report, indent=2))
    return int(report["passed"] < report["total"])


if __name__ == "__main__":
    raise SystemExit(main())
