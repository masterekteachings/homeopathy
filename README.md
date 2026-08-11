# Homeopathy Classes — Master E.K. Teachings

Public learner-facing publication of the Homeopathy teaching collection.

Canonical learner site: `https://masterekteachings.github.io/homeopathy/`

Optional noncanonical draft preview: `https://masterekteachings.github.io/homeopathy/preview/`

The canonical Reader is rebuilt from the current production source repository and publishes each learner-facing Philosophy bundle only after its English, Telugu and Russian notes are all explicitly marked `note_status: complete` after final publication QC. Draft or merely source-checked bundles do not appear at the canonical URL.

The learner homepage may identify an upcoming teaching series, but unfinished lecture rows are not exposed in the canonical Reader. First-time visitors now open the Reader in English; an explicitly selected Telugu or Russian preference is remembered. Page-color preferences, reading-language preference and core navigation are shared across the learner site. Homepage language selection visibly localizes learner-facing interface copy and lecture topic cues while preserving the source course identifiers. Browser metadata is learner-facing as well. Lecture pages include a quiet multilingual "In this lecture" outline derived directly from the selected note's section headings, with Previous/Next navigation retained for sequential study.

The `/preview/` surface may expose work that has not yet passed the canonical publication gate; it must never be used as evidence that a lecture passed final QC.

Internal transcripts, QC evidence, automation, prompts, provider outputs and the project dashboard are not published here.

## Publication model

`vamsikrishnajallipalli/master-ek-homeo-notes` remains the production/source repository. This repository acts as the clean publication surface.

The Pages workflow can be run manually and also checks for new production changes on a schedule. Each build:

1. checks out the current production `main`;
2. builds the noncanonical `/preview/` from the available trilingual draft set;
3. removes every non-final Philosophy bundle from the canonical build unless EN+TE+RU all say `note_status: complete`;
4. removes internal project-control UI from the public build;
5. publishes the canonical Reader at `/homeopathy/` and the draft preview at `/homeopathy/preview/`;
6. writes canonical `status.json` so the root Master E.K. Teachings portal can show release coverage without hand-maintained counts.
