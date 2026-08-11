# Enrichment build checkpoint

The learner-facing **Explore & search** publication chain has now passed its non-deploying integration validation against current production source after repairing unsupported localized anchors.

Validated chain:

- final-QC-gated 38/38 Philosophy source checkout;
- strict multilingual enrichment anchor validation;
- generated semantic entity catalog/index;
- generated selected-language passage-search index;
- public App transformation that removes the internal project dashboard while preserving Explore;
- TypeScript/Vite learner build;
- final artifact assertion confirming 38/38 canonical Philosophy coverage.

This commit intentionally triggers the real GitHub Pages publication with the same validated publisher/source chain.

Learner surface included:

- selected-language passage search across completed Philosophy notes;
- concept/remedy/person/text/place browsing from curated entity evidence;
- entity pages with lecture-by-lecture occurrence context and backlinks;
- deep links from search results to the matching lecture section;
- deep links from entity occurrences to the matching inline companion mention.
