# Enrichment build checkpoint

The learner-facing **Explore & search** publication chain is validated across the evidence-backed 38/38 Philosophy corpus.

This branch exists only to obtain an inspectable pull-request CI result for the **final M4 Philosophy enriched learning edition**. It does not introduce a separate learner feature.

The production source now includes:

- 38/38 final trilingual Philosophy Core Study Notes;
- selected-language passage search and entity Explore/backlinks;
- reviewed-only cross-lecture teaching progression for the major method, miasm and remedy arcs, including Nyāsa Vidyā, Sycosis, the syphilitic miasm and Hering's direction-of-cure teaching;
- the source-fidelity correction restoring the omitted Nyāsa/Science of Correspondences opening in Russian Lecture 029;
- localized English/Telugu/Russian inline study-companion interface;
- selective sourced study context rather than decorative filling, including the public-domain Hering portrait and a public-domain historical scan of Hahnemann's *The Chronic Diseases*.

The PR workflows must rebuild against current production `main`, run strict enrichment/progression validation, compile the learner Reader, assert canonical 38/38 coverage, and smoke-test the deployed learner markers. A passing result is the evidence gate for closing M4 and making Materia Medica the active main milestone.
