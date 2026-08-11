# Homeopathy Classes — Master E.K. Teachings

Public learner-facing publication of the Homeopathy teaching collection.

Canonical learner site: `https://masterekteachings.github.io/homeopathy/`

Owner project command center: `https://masterekteachings.github.io/homeopathy/#/project` (unlinked from learner navigation)

Optional noncanonical draft preview: `https://masterekteachings.github.io/homeopathy/preview/`

The canonical Reader is rebuilt from the current production source repository and publishes each learner-facing Philosophy bundle only after its English, Telugu and Russian notes are all explicitly marked `note_status: complete` after final publication QC. Draft or merely source-checked bundles do not appear as learner lecture rows at the canonical URL.

The learner homepage may identify an upcoming teaching series, but unfinished lecture rows are not exposed in the canonical Reader. First-time visitors open the Reader in English; an explicitly selected Telugu or Russian preference is remembered. Page-color preferences, reading-language preference and core navigation are shared across the learner site. Homepage language selection visibly localizes learner-facing interface copy and lecture topic cues while preserving the source course identifiers. Browser metadata is learner-facing as well. Lecture pages include a quiet multilingual "In this lecture" outline derived directly from the selected note's section headings, with Previous/Next navigation retained for sequential study.

The `/preview/` surface may expose work that has not yet passed the canonical publication gate; it must never be used as evidence that a lecture passed final QC.

Internal transcripts, QC evidence, automation, prompts and provider outputs are not published as learner content. The owner command center is deliberately retained at the unlinked `#/project` route so project milestones, repository-derived lecture telemetry, blockers, inactive lanes, branch hygiene and next actions can be inspected from the same deployed source revision without adding project-control links to the learner interface.

## Publication model

`vamsikrishnajallipalli/master-ek-homeo-notes` remains the production/source repository. This repository acts as the clean publication surface.

The Pages workflow can be run manually and also checks for new production changes on a schedule. Each build:

1. checks out the current production `main`;
2. validates the curated multilingual enrichment evidence and generates the derived enrichment/search/progression indexes;
3. generates the owner lecture-pipeline telemetry used only by the unlinked `#/project` route;
4. builds the noncanonical `/preview/` from the available trilingual draft set;
5. removes every non-final Philosophy bundle from the canonical learner release unless EN+TE+RU all say `note_status: complete` and accepted final evidence exists;
6. retains the owner project-control route without exposing it in learner navigation;
7. publishes the canonical Reader at `/homeopathy/` and the draft preview at `/homeopathy/preview/`;
8. writes canonical `status.json`, including the source commit and owner-dashboard route, so publication state remains inspectable.
