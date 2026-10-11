# Campus Comps case: working folder

This folder holds everything an AI coding agent needs to finish the Campus Comps teaching case. In the case, students direct an AI coding agent to build a data website from the College-town home sales dataset and publish it with GitHub Pages. There are three variations of the case: Open Brief, Specific Questions and General Instructions.

## How to start

Open this folder in your AI coding agent and give it this instruction:

> Read HANDOFF.md from start to finish, then follow it.

The handoff is self-contained. It says what already exists, what to build, the checks to run, and when to stop and ask.

## What's here

| Path | What it is |
|---|---|
| `HANDOFF.md` | Instructions for the coding agent |
| `inputs/college-town-dataset/` | The dataset package (version 1.0): data in five formats, the data description sheet, build notes, instructor reference figures and build scripts |
| `inputs/college-town-dataset/build/export_raw.py` | Exports the two raw build inputs from the source database and checks that they rebuild the published data exactly (see below) |
| `inputs/case-documents/` | The three student case documents, the GitHub Pages setup guide, and `source/` (the script that builds them) |
| `inputs/sample-sites/` | Two finished sample sites: Variation 2 (`v2-six-questions`) and Variation 3 (`v3-close-to-campus`) |
| `output/` | Where the agent writes the finished case package |

## Raw build inputs

The dataset is built from two raw extracts of the source database, `build/raw_extract.csv` and `build/raw_events.csv`. Export them once from your own machine, because the export needs your database login:

```bash
cd inputs/college-town-dataset
pip install "psycopg[binary]" pandas openpyxl pyarrow duckdb
export DATABASE_URL='postgresql://...'   # from the PlanetScale dashboard; never save it in a file here
python build/export_raw.py --verify
```

The script writes both files into `build/`, checks their row counts (35,822 and 284,955), rebuilds the dataset in a temporary folder, and reports PASS if the rebuilt CSV is byte-identical to the published one. The files contain the listing site's property IDs.

## Public repository

This folder is meant to be pushed to a public GitHub repository, and nothing in it is hidden. That includes the dataset, the instructor materials and the answer key once they are built. `.gitignore` lists only operating system and Python clutter, such as `.DS_Store` and `__pycache__`.

## Data citation

College-town home sales dataset, version 1.0 (2026). University of Illinois-Deloitte Foundation Center for Business Emerging Technologies. Data collected March 2026.
