#!/usr/bin/env python3
"""Build a learner-facing Homeopathy Reader from the production source repo.

The production repository remains the source of truth. This script runs only in
the publication repository's GitHub Actions checkout and mutates the disposable
source checkout before building. Internal project-control UI and pipeline status
are deliberately excluded from the compiled public site.

Modes:
- ``final`` (default): a Philosophy lecture is included only when English,
  Telugu and Russian are all explicitly ``note_status: complete`` AND matching
  final-QC evidence records an independently accepted review against
  ``EDITORIAL_QC.md``.
- ``preview``: the complete trilingual draft set can be rendered at the
  explicitly noncanonical ``/preview/`` surface without rewriting draft status.

Structural validity, file existence, or preview visibility never imply final QC.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: build_public_reader.py <source-repo-checkout> <output-dir>")

SOURCE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
READER = SOURCE / "reader"
MODE = os.environ.get("MASTER_EK_PUBLICATION_MODE", "final").strip().lower() or "final"
if MODE not in {"final", "preview"}:
    raise SystemExit(f"unsupported MASTER_EK_PUBLICATION_MODE={MODE!r}")


def replace_required(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"public-build guard failed: {label} marker not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def frontmatter_value(path: Path, key: str) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---\n"):
        return None
    for line in text.splitlines()[1:]:
        if line == "---":
            break
        if ":" not in line:
            continue
        k, raw = line.split(": 1) if False else line.split(":", 1)
        if k.strip() == key:
            return raw.strip().strip('"').strip("'")
    return None


def note_files(position: int, directory: Path) -> list[Path]:
    return list(directory.glob(f"{position:03d}-*.md"))


def final_evidence_valid(position: int) -> bool:
    path = SOURCE / "corpus" / "qc" / "final" / f"{position:03d}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    if data.get("position") != position or data.get("status") != "complete":
        return False
    if data.get("standard") != "EDITORIAL_QC.md":
        return False
    if not data.get("editorial_pass") or not data.get("independent_review"):
        return False
    review = data.get("review")
    if not isinstance(review, dict) or review.get("ready") is not True:
        return False
    assessment = review.get("uncertainty_assessment")
    if not isinstance(assessment, dict) or assessment.get("reviewed") is not True:
        return False
    if assessment.get("blocking") is not False:
        return False
    issues = review.get("issues", [])
    if not isinstance(issues, list):
        return False
    return not any(isinstance(issue, dict) and issue.get("severity") == "blocking" for issue in issues)


def included_positions() -> list[int]:
    """Return Philosophy positions allowed in the selected publication mode."""
    included: list[int] = []
    dirs = [SOURCE / "notes", SOURCE / "notes" / "te", SOURCE / "notes" / "ru"]
    for position in range(1, 39):
        trios = [note_files(position, directory) for directory in dirs]
        if not all(len(files) == 1 for files in trios):
            continue
        if MODE == "preview":
            included.append(position)
            continue
        if all(frontmatter_value(files[0], "note_status") == "complete" for files in trios) and final_evidence_valid(position):
            included.append(position)
    return included


# Strip every Philosophy note that is not allowed in this build mode before
# Reader metadata is generated. Canonical mode is evidence-gated; preview mode
# keeps the real draft/source-checked frontmatter intact.
ready_before_build = set(included_positions())
for position in range(1, 39):
    if position in ready_before_build:
        continue
    for directory in (SOURCE / "notes", SOURCE / "notes" / "te", SOURCE / "notes" / "ru"):
        for path in note_files(position, directory):
            path.unlink()

# Remove the internal owner/project dashboard from the public application.
app = READER / "src" / "App.tsx"
replace_required(app, 'import ProjectDashboard from "./components/ProjectDashboard";\n', "", "dashboard import")
replace_required(app, 'import "./project-dashboard.css";\n', "", "dashboard stylesheet")
replace_required(
    app,
    'type Route =\n  | { view: "library" }\n  | { view: "lecture"; position: number }\n  | { view: "project" };',
    'type Route =\n  | { view: "library" }\n  | { view: "lecture"; position: number };',
    "project route type",
)
replace_required(app, '  if (/^#\\/project\\/?$/.test(hash)) return { view: "project" };\n', "", "project route parser")
replace_required(
    app,
    '    <div className={`app-shell${route.view === "project" ? " project-shell" : ""}`}>',
    '    <div className="app-shell">',
    "project shell class",
)
replace_required(
    app,
    '      ) : route.view === "project" ? (\n        <ProjectDashboard />\n      ) : (',
    '      ) : (',
    "project dashboard render branch",
)

# The public build does not generate the internal pipeline dashboard data.
package_path = READER / "package.json"
package = json.loads(package_path.read_text(encoding="utf-8"))
package["scripts"]["meta"] = "node scripts/build-library.mjs"
package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Build specifically for the clean public project-site URL. The workflow
# rewrites this base in the disposable preview artifact to /homeopathy/preview/.
(READER / "vite.config.ts").write_text(
    "import { defineConfig } from 'vite'\n"
    "import react from '@vitejs/plugin-react'\n"
    "import path from 'node:path'\n\n"
    "export default defineConfig(({ command }) => ({\n"
    "  plugins: [react()],\n"
    "  base: command === 'build' ? '/homeopathy/' : '/',\n"
    "  server: { fs: { allow: [path.resolve(import.meta.dirname, '..')] } },\n"
    "}))\n",
    encoding="utf-8",
)

# Remove generic product-instruction copy; retain language fallback messaging
# only when it is actually needed for the selected lecture/language.
lecture = READER / "src" / "components" / "LectureView.tsx"
old_subtitle = '''        <p className="app-subtitle">\n          Read the study note start to finish; optional companion notes\n          provide extra context.\n          {noteState.fallback &&\n            ` This lecture's note is not yet available in ${LANGUAGES.find((l) => l.id === noteState.language)?.label ?? "the selected language"} — showing the English note.`}\n        </p>'''
new_subtitle = '''        {noteState.fallback && (\n          <p className="app-subtitle">\n            {`This lecture's note is not yet available in ${LANGUAGES.find((l) => l.id === noteState.language)?.label ?? "the selected language"} — showing the English note.`}\n          </p>\n        )}'''
replace_required(lecture, old_subtitle, new_subtitle, "learner subtitle")

# Reproducible public build.
subprocess.run(["npm", "ci", "--no-audit", "--no-fund"], cwd=READER, check=True)
subprocess.run(["npm", "run", "build"], cwd=READER, check=True)

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(READER / "dist", OUT)
(OUT / ".nojekyll").write_text("", encoding="utf-8")

ready = sorted(ready_before_build)
status = {
    "collection": "homeopathy",
    "source_repository": "vamsikrishnajallipalli/master-ek-homeo-notes",
    "source_commit": os.environ.get("SOURCE_COMMIT", ""),
    "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "languages": ["te", "en", "ru"],
}
if MODE == "final":
    status.update({
        "release_stage": "final-qc-gated",
        "qc_passed_trilingual_philosophy": len(ready),
        "trilingual_philosophy_total": 38,
        "qc_passed_trilingual_philosophy_positions": ready,
        "publication_gate": "EN+TE+RU note_status complete + accepted corpus/qc/final evidence",
    })
else:
    status.update({
        "release_stage": "preview",
        "preview_trilingual_philosophy": len(ready),
        "trilingual_philosophy_total": 38,
        "preview_trilingual_philosophy_positions": ready,
        "publication_gate": "NONCANONICAL PREVIEW: trilingual draft visibility does not imply final QC",
    })
(OUT / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

print(f"Public Homeopathy Reader ({MODE}) built from {status['source_commit'][:12] or 'current checkout'}")
if MODE == "final":
    print(f"Final-QC trilingual Philosophy coverage: {len(ready)}/38")
else:
    print(f"Noncanonical trilingual Philosophy preview coverage: {len(ready)}/38")
