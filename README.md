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
| `inputs/case-documents/` | The three student case documents, the GitHub Pages setup guide, and `source/` (the script that builds them) |
| `inputs/sample-sites/` | Two finished sample sites: Variation 2 (`v2-six-questions`) and Variation 3 (`v3-close-to-campus`) |
| `output/` | Where the agent writes the finished case package |

## Public repository

This folder is meant to be pushed to a public GitHub repository, and nothing in it is hidden. That includes the dataset, the instructor materials and the answer key once they are built. `.gitignore` lists only operating system and Python clutter, such as `.DS_Store` and `__pycache__`.

## Data citation

College-town home sales dataset, version 1.0 (2026). University of Illinois-Deloitte Foundation Center for Business Emerging Technologies. Data collected March 2026.
