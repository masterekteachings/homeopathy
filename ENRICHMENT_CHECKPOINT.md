# Enrichment build checkpoint

The production source now has an authored semantic mention bundle for every final Philosophy lecture, 001–038.

This publisher push intentionally forces a fresh Reader build against current production `main` so the build-time enrichment validator can reject stale multilingual anchors or registry references before learner-facing Explore/navigation is enabled.

Explore remains hidden until validation and cross-lecture backlink review are complete.
