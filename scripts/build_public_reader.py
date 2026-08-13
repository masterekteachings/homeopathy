#!/usr/bin/env python3
"""Build the learner-facing Homeopathy site from the production source repo.

Canonical mode publishes only evidence-backed trilingual Philosophy notes.
Preview mode can render the complete trilingual draft set at /preview/.
The public build is learner-only: internal dashboards, telemetry and production
machinery are removed before the Reader is built.
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
        k, raw = line.split(":", 1)
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
    return not any(
        isinstance(issue, dict) and issue.get("severity") == "blocking"
        for issue in issues
    )


def included_positions() -> list[int]:
    included: list[int] = []
    dirs = [SOURCE / "notes", SOURCE / "notes" / "te", SOURCE / "notes" / "ru"]
    for position in range(1, 39):
        trios = [note_files(position, directory) for directory in dirs]
        if not all(len(files) == 1 for files in trios):
            continue
        if MODE == "preview":
            included.append(position)
            continue
        if (
            all(frontmatter_value(files[0], "note_status") == "complete" for files in trios)
            and final_evidence_valid(position)
        ):
            included.append(position)
    return included


ready_before_build = set(included_positions())
for position in range(1, 39):
    if position in ready_before_build:
        continue
    for directory in (SOURCE / "notes", SOURCE / "notes" / "te", SOURCE / "notes" / "ru"):
        for path in note_files(position, directory):
            path.unlink()

prepare_script = SOURCE / "scripts" / "prepare_public_reader.py"
if not prepare_script.exists():
    raise SystemExit(f"missing learner-only publication preparer: {prepare_script}")
subprocess.run([sys.executable, str(prepare_script), str(SOURCE)], check=True)

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
    "publication_surface": "learner-only",
}
if MODE == "final":
    status.update({
        "release_stage": "final-qc-gated",
        "qc_passed_trilingual_philosophy": len(ready),
        "trilingual_philosophy_total": 38,
        "qc_passed_trilingual_philosophy_positions": ready,
    })
else:
    status.update({
        "release_stage": "preview",
        "preview_trilingual_philosophy": len(ready),
        "trilingual_philosophy_total": 38,
        "preview_trilingual_philosophy_positions": ready,
    })
(OUT / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

for forbidden in (
    "ProjectDashboard",
    "owner_dashboard_route",
    "raw.githubusercontent.com/vamsikrishnajallipalli/master-ek-homeo-notes",
    "#/project",
    "VAMSI_AI_MODUS_OPERANDI",
):
    for path in OUT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".css", ".json", ".map"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if forbidden in text:
            raise SystemExit(f"forbidden internal publication marker {forbidden!r} in {path}")

print(f"Public Homeopathy Reader ({MODE}) built from {status['source_commit'][:12] or 'current checkout'}")
print(f"Trilingual Philosophy coverage: {len(ready)}/38")
print("Learner-only publication surface verified")
