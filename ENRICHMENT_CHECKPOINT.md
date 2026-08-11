# Enrichment build checkpoint

The production source now has an authored and previously validated semantic mention bundle for every final Philosophy lecture, 001–038.

This publisher push intentionally forces a fresh Reader build against the current production `main` after adding the learner-facing **Explore & search** surface:

- selected-language passage search across completed Philosophy notes;
- concept/remedy/person/text/place browsing from curated entity evidence;
- entity pages with lecture-by-lecture occurrence context and backlinks;
- deep links from search results to the matching lecture section;
- deep links from entity occurrences to the matching inline companion mention.

The publication build remains the integrity gate: enrichment validation, generated indexes, TypeScript and Vite must all pass before this surface is treated as deployable.
