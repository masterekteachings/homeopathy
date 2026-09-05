# Master E.K. Homeopathy Teachings

**A multilingual digital learning library built from the recorded homoeopathy classes of Ekkirala Krishnamacharya, widely known as Master E.K.**

➡️ **Start learning:** https://masterekteachings.github.io/homeopathy/

This repository is the **public, learner-facing publication layer** of the Master E.K. Learning Library. It turns a large recorded teaching corpus into a calm, searchable and source-grounded study experience while preserving the sequence, terminology, examples and reasoning of the original classes.

> **Study and historical reference only. This library is not medical advice and is not a substitute for professional medical care.**

## What is this project?

Master E.K.'s homoeopathy teachings exist across a substantial collection of recorded classes. The aim of this project is to make those classes easier to study without reducing them to short summaries or disconnected quotations.

The complete Homeopathy collection currently being organised covers **117 classes** in the original teaching order:

| Series | Classes |
|---|---:|
| Junior Philosophy | 13 |
| Senior Philosophy | 25 |
| Materia Medica | 79 |
| **Total** | **117** |

The Reader publishes only classes that have passed the project's source-fidelity and review gates. The live site therefore shows the **currently accepted learner release**, while the remaining corpus continues through production and review.

## What does a learner get?

The learning experience is designed around four complementary views:

- **Synopsis** — a structured study companion that helps a learner understand and revise the class;
- **Notes** — the complete faithful class text, preserving the teaching rather than compressing it into a summary;
- **Watch / Listen** — the source recording where available and authorised;
- **Explore** — progressively richer links between concepts, remedies, symptoms, people, texts and related lectures.

The project is multilingual. Current production and publication work includes **English, Telugu, Russian, French, German and Dutch/Flemish**, with release requirements varying by stage as the corpus matures.

## What are we trying to preserve?

The goal is not to rewrite Master E.K. into a modern textbook voice. A trustworthy learner edition should preserve, where present in the source:

- the reasoning and order in which a subject is taught;
- definitions and distinctions;
- examples, cases and analogies;
- remedy, symptom and concept relationships;
- Sanskrit, Telugu, English and other terminology used in the class;
- references to people, books and scriptures;
- useful audience interaction;
- humour, turns of phrase and teaching personality when they carry learning value.

Sequence is part of the teaching, not merely packaging.

## How is trust handled?

A file existing in the repository is **not** enough for publication.

The production system separates source evidence, reconciled class text, learner artifacts, editorial review and independent QC. A class becomes learner-visible only after the applicable publication gate has passed. Genuine uncertainty is preserved or escalated rather than silently invented away.

The public site is intentionally separated from the private production factory so internal prompts, model/provider outputs, raw working files, QC machinery and operational telemetry do not become learner content.

## Public architecture

- **This repository:** clean public release surface for the Homeopathy collection
- **Live Reader:** https://masterekteachings.github.io/homeopathy/
- **Broader project:** Master E.K. Learning Library, designed to support additional teaching collections over time

The source playlist ordering is preserved so a learner can study the corpus sequentially rather than encountering an algorithmically rearranged set of excerpts.

## For maintainers

The production/source repository is separate from this public repository. Publication creates a sanitized learner snapshot after the relevant acceptance gates pass.

The current publication pipeline validates the learner release, removes non-final lecture bundles from the canonical site, generates the Reader assets and records publication state. Draft/preview artifacts are never evidence that a lecture has passed final QC.

If you are working on the production system, use the project nerve-centre documents in the private factory rather than this README for current runtime status and changing acceptance counts.

---

**Master E.K. Learning Library** — preserving recorded teaching as a trustworthy, multilingual learning corpus.