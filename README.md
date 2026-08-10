# Homeopathy Classes — Master E.K. Teachings

Public learner-facing publication of the Homeopathy teaching collection.

Live site target: `https://masterekteachings.github.io/homeopathy/`

The public Reader is rebuilt from the current production source repository and contains only learner-facing material. Internal transcripts, QC evidence, automation, prompts, provider outputs and the project dashboard are not published here.

## Publication model

`vamsikrishnajallipalli/master-ek-homeo-notes` remains the production/source repository. This repository acts as the clean publication surface.

The Pages workflow can be run manually and also checks for new production changes on a schedule. Each build:

1. checks out the current production `main`;
2. removes internal project-control UI from the public build;
3. builds the learner-facing Reader for `/homeopathy/`;
4. publishes the static artifact to GitHub Pages;
5. writes `status.json` so the root Master E.K. Teachings portal can show current release coverage without hand-maintained counts.
