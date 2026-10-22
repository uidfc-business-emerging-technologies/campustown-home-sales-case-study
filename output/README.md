# Campus Comps case package

The finished case package for "Campus Comps: Building a Data Website with an AI Coding Agent". `REPORT.md` describes what was built, how it was checked and what is left to decide.

| Folder | For | What it holds |
|---|---|---|
| `students/` | Students | The three case documents, the setup guide, the data description sheet (Word and markdown) and the dataset in five formats |
| `instructor/` | Instructors | The instructor orientation, the Variation 2 answer key (Word and Excel), the post-assignment survey, the reference code and one reference site per variation |
| `source/` | The case author | The source and build scripts for every Word document |
| `dataset/` | The case author | The corrected dataset package, version 1.0: the data, the description sheet, the build notes and the build scripts. It replaces the package in `inputs/`; see `REPORT.md`, section 6 |
| `report-screenshots/` | The case author | The reference sites at 375 and 1280 pixels, light and dark, from the final browser test |

Give each student only their variation's case document and the setup guide. Students create their repositories from the starter template, [campus-comparables-template](https://github.com/uidfc-business-emerging-technologies/campus-comparables-template), which gives them the data and the description sheet.

## Rebuild everything

1. **Figures, answer key, orientation figures and site data** (Python 3.11 or later):

    ```bash
    cd instructor/reference-code
    pip install -r requirements.txt
    python run_all.py
    ```

2. **Case documents and setup guide**, after editing `source/case-documents/content.js` (Node.js):

    ```bash
    cd source/case-documents
    npm install docx@9.7.1
    node build.js ../../students
    ```

3. **Every other Word document**: the description sheet, answer key, orientation and survey.

    ```bash
    cd source/word-documents
    npm install docx@9.7.1
    node build.js
    ```

The orientation's text is in `source/word-documents/templates/instructor_orientation.md`; edit that file, not the filled-in copy, and run steps 1 and 3. The answer key's markdown is written by step 1; change `instructor/reference-code/answer_key.py` instead of editing it.
