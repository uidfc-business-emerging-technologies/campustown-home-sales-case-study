// Content for the Campus Comps case documents and setup guide.
// Inline markup: **bold**, [[code]]. Plain ASCII only: no em or en dashes, straight quotes.

const TITLE = "Campus Comps: Building a Data Website with an AI Coding Agent";
const AUTHOR = "[Author name]";
const CENTER = "University of Illinois-Deloitte Foundation Center for Business Emerging Technologies";
const FUNDING = "Funded by the " + CENTER + ".";
const CITATION = "College-town home sales dataset, version 1.0 (2026). " + CENTER + ". Data collected March 2026.";
const LICENSE = "This case is shared under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license (CC BY-NC-SA 4.0).";
const TEMPLATE_URL = "https://github.com/uidfc-business-emerging-technologies/campus-comparables-template";

// ---------------------------------------------------------------------------
// Shared sections, before "Your task"
// ---------------------------------------------------------------------------
const SHARED_BEFORE = [
  { t: "h1", text: "Overview" },
  { t: "p", text: "AI coding agents can now write most of the code for a data website. That changes the analyst's job. You decide what to show and who it is for, you direct the agent, and you check that every number is right." },
  { t: "p", text: "In this case, you will do all three with real data on home sales around 11 university campuses. You will publish your work as a public website on GitHub Pages." },

  { t: "h1", text: "Learning objectives" },
  { t: "p", text: "By the end of this case, you will be able to:" },
  { t: "ul", items: [
    "Direct an AI coding agent to build a data website from plain HTML, CSS and JavaScript",
    "Explore an unfamiliar real-world dataset and handle its data quality problems",
    "Choose and design visualizations that communicate findings to an audience",
    "Check AI-produced analysis independently",
    "Publish and update a website with GitHub and GitHub Pages",
  ] },

  { t: "h1", text: "The data" },
  { t: "p", text: "You will work with the College-town home sales dataset (version 1.0). It holds 35,442 completed home sales around 11 university campuses, in 18 cities across 11 states, collected in March 2026." },
  { t: "p", text: "Each row is one sale. It records:" },
  { t: "ul", items: [
    "Where the home is",
    "The dates it was listed, went under contract and sold",
    "The sale price",
    "The home's size and features",
    "Its tax assessment",
    "The nearest campus and the straight-line distance to it",
  ] },
  { t: "p", text: "The data comes as CSV, Excel, SQLite, DuckDB and Parquet files, with identical values in each. All five are already in the starter repository you will create (see \"Getting started\"). For a website, the CSV file (about 9 MB) is the simplest choice. The Parquet file is smaller (about 2 MB), but reading it in a browser takes an extra library." },
  { t: "p", text: "**Read the data description sheet before you start, and give it to your agent before it writes any analysis code.** The sheet explains every column. It also explains, under \"Five things that will bite you,\" five problems in the data that will trip up any analysis that ignores them:" },
  { t: "ol", items: [
    "**Days on market** runs from [[list_date]] to [[contract_date]], not to [[sale_date]]. About one sale in five is missing one of those dates, and a blank date is not zero.",
    "**Street addresses repeat** because condo and apartment units share an address. Never remove duplicates by address.",
    "**Some prices are impossible.** They range from $0 to $81.5 million. Choose a rule for which sales to include, and state it.",
    "**The [[home_type]] column is unreliable.** Don't build an analysis on it.",
    "**Some values are impossible on their face.** For example, some homes have 0 square feet of living area.",
  ] },
];

// ---------------------------------------------------------------------------
// Variation-specific "Your task" sections
// ---------------------------------------------------------------------------
const TASK_V1 = [
  { t: "h1", text: "Your task" },
  { t: "p", text: "Build a website with visualizations using the College-town home sales dataset." },
  { t: "p", text: "What it is about, who it is for, how it looks and how it works are up to you. It can be one page or several, analytical or playful, and focused on one town or on all of them." },
  { t: "p", text: "The only requirements are the build and publish requirements below and the items under \"What to submit.\"" },
];

const TASK_V2 = [
  { t: "h1", text: "Your task" },
  { t: "p", text: "Build a website that answers the six questions below." },
  { t: "p", text: "For each question, your site must show:" },
  { t: "ul", items: [
    "The figures that answer it",
    "At least one chart",
    "One or two sentences that answer the question in plain words",
  ] },
  { t: "p", text: "Write the answers for a general reader, such as someone thinking about moving to one of these towns. You may arrange the answers in any order and layout, and add anything else you like. Your site must also have a Data notes section that restates the definitions below." },
  { t: "h2", text: "Definitions" },
  { t: "p", text: "Use these definitions so every answer can be checked. They take the place of the rules that \"The data\" section asks you to choose." },
  { t: "ul", items: [
    "**Campus area:** the [[university]] column. There are 11 campus areas.",
    "**Valid sale:** a sale with a [[sale_price]] of $1,000 or more. Use only valid sales for figures that involve [[sale_price]] (Questions 1, 3 and 5). The other questions use every sale.",
    "**Price per square foot:** [[sale_price]] divided by [[living_area_sqft]]. Compute it for each valid sale with a living area of at least 100 square feet, then take the median of those values. (Dividing a median price by a median living area gives a different, wrong answer.)",
    "**Days on market:** the number of days from [[list_date]] to [[contract_date]], for sales that have both dates. A blank date is never zero.",
    "**Distance bands,** based on [[miles_to_campus]]:",
    { sub: [
      "Under 1 mile",
      "1 to under 2 miles",
      "2 to under 5 miles",
      "5 to under 10 miles",
      "10 miles or more",
    ] },
    "**Small groups:** if a median or a share is based on fewer than 20 sales, show \"fewer than 20 sales\" in place of it. Always show counts of sales and addresses.",
    "**Medians, not means,** unless a question says otherwise.",
  ] },
  { t: "h2", text: "Questions" },
  { t: "ol", items: [
    "**Price levels.** For each campus area, what are the median sale price and the median price per square foot? Which areas are highest and lowest on each measure? Does the ranking change between the two measures, and why might it?",
    "**Speed.** For each campus area, what is the median days on market? What share of sales has no days on market because a date is missing? Which areas sell fastest, and how could the missing share affect the comparison?",
    "**Distance.** For each campus area, what is the median price per square foot in each distance band? In most areas, does price per square foot fall as the distance from campus grows? Say what you count as falling, and name any area where it does not.",
    "**Timing.** Across all areas, pooled together, what is the median days on market for each calendar month in which homes were listed? Use only homes listed from April 1, 2023 through March 31, 2025, so that each calendar month covers exactly two years. Group them by the month of [[list_date]]. Which months are fastest, and which are slowest?",
    "**Assessment.** For each campus area, what is the median ratio of [[tax_assessed_value]] to [[sale_price]], for valid sales with an assessed value above 0? Which areas are far from 1 (say what you count as far), and what could explain the gap? Cite a source for any explanation.",
    "**Buildings.** Group sales by street address, city, state and ZIP code. In each campus area, how many addresses have more than one sale, and how many sales do they cover? How does the median [[miles_to_campus]] of those sales compare with that of all other sales, across all areas and within each area?",
  ] },
];

const TASK_V3 = [
  { t: "h1", text: "Your task" },
  { t: "p", text: "Choose one question about the data that matters to a specific kind of user, such as a first-time buyer, a new faculty member or a city planner. Build a website that answers it." },
  { t: "p", text: "Your site must:" },
  { t: "ol", items: [
    "State its question and its user at the top of the first page.",
    "Show at least three headline numbers that answer the question.",
    "Include at least two charts, tables or maps, with at least one control that changes them, such as a campus picker or a price range.",
    "Have a Data notes section that says which rows you left out and why, and how each figure is defined.",
  ] },
  { t: "h2", text: "A suggested process" },
  { t: "p", text: "This process is recommended, but not graded." },
  { t: "ol", items: [
    "Read the data description sheet, then ask your agent to profile the data: what each column holds, how complete it is, and what looks odd.",
    "Write down three candidate questions, then pick the one the data answers most clearly.",
    "Sketch your page on paper before you prompt the agent.",
    "Publish a placeholder page on your first day.",
    "Build in small steps, and check each headline number with a separate calculation.",
    "Ask someone who has not seen your site to use it for two minutes, then fix whatever confused them.",
  ] },
];

// ---------------------------------------------------------------------------
// Shared sections, after "Your task"
// ---------------------------------------------------------------------------
const SHARED_AFTER = [
  { t: "h1", text: "Build and publish requirements" },
  { t: "p", text: "Whatever you build must meet these requirements:" },
  { t: "ul", items: [
    "**Plain HTML, CSS and JavaScript only.** Don't use frameworks such as React, Vue or Svelte, a build step, or server-side code. You may load JavaScript libraries, such as a charting or mapping library, with a script tag.",
    "**A public GitHub repository** holds all of the site's files.",
    "**GitHub Pages publishes the site.** It must load at its github.io address without a login.",
    "**The site reads its data from files in the repository.** If you prepare summary files from the full dataset, commit the script that made them and the data file it reads, so anyone can reproduce them. A script that prepares data files is fine; the site itself must run without a build step.",
    "**The site works on a phone** and loads without errors in a private browser window.",
    "**The site cites the dataset** (see \"Citation and license\").",
  ] },

  { t: "h1", text: "Working with your AI coding agent" },
  { t: "p", text: "You may use any AI coding agent or assistant, and you may also edit code by hand. Tools change quickly, so this case does not give steps for any particular one. Use your agent's own documentation to install it and connect it to your project. The setup guide describes a way of working that suits any agent." },
  { t: "p", text: "Whatever tool you use, you are responsible for what it produces:" },
  { t: "ul", items: [
    "Every team member must be able to explain how each number on the site is computed.",
    "Never put passwords, API keys or other secrets in your repository or your site's code.",
    "Commit your work as you go, so your repository's history shows how the site developed.",
    "Keep an agent log (see \"What to submit\").",
  ] },

  { t: "h1", text: "What to submit" },
  { t: "p", text: "Submit the following through the method your instructor specifies. Teams submit once." },
  { t: "ol", items: [
    "**Your repository's URL.** The repository must be public.",
    "**Your site's URL** (its github.io address).",
    "**A README.md file** in your repository. The starter repository's README has a section for each item below. Fill them all in, and delete its \"Start here\" section:",
    { sub: [
      "What the site is for: its question and audience, or a short description",
      "The live URL",
      "How to preview the site on your own computer",
      "Data notes: which rows you left out and why, and how each figure is defined",
      "\"How we checked our numbers\": at least three numbers shown on the site, each with a calculation that confirms it and is separate from the site's own code, such as a spreadsheet formula, a SQL query or a short script",
      "The tools you used",
      "The dataset citation",
      "For teams, who did what",
    ] },
    "**An AGENT_LOG.md file** in your repository, with dated entries. Each entry records what you asked the agent (paste in your key prompts), what it produced, and what you checked or changed. Include at least one time the agent got something wrong, and how you caught it. The starter repository's [[AGENT_LOG.md]] gives the outline for an entry.",
    "**A reflection of 400 to 600 words** that answers these questions. Submit it to your instructor; it does not go in your repository.",
    { sub: [
      "Which decisions did you make, and which did the agent make?",
      "Where did the agent's output need correcting, and how did you notice?",
      "How did you decide what to show, and what did you leave out?",
      "What would you do differently next time?",
    ] },
  ] },
  { t: "p", text: "Your instructor may also ask for a demo video of three minutes or less." },

  { t: "h1", text: "How you will be graded" },
  { t: "table", widths: [2300, 1000, 6060], header: ["Criterion", "Points", "Full credit"], rows: [
    ["Accuracy", "25", "Numbers on the site can be reproduced from the data, using the definitions the site states or, where this case sets definitions, using those."],
    ["Data handling", "15", "The data problems that affect the site's numbers are handled correctly and explained in the data notes."],
    ["Communication", "20", "A visitor understands the site's purpose within 10 seconds. Findings are stated in words, and the content suits its audience."],
    ["Visualization", "20", "Chart types fit the data. Axes and units are labeled, charts are readable on a phone, and controls work."],
    ["Engineering and publishing", "10", "The GitHub Pages site loads, the repository is tidy, the README is complete, and there are no secrets in any file."],
    ["Agent process and reflection", "10", "The agent log shows you directing and checking the agent, and the reflection is specific."],
    ["**Total**", "**100**", ""],
  ] },

  { t: "h1", text: "Suggested schedule" },
  { t: "p", text: "Your instructor will give you exact dates. For a two-week case:" },
  { t: "ul", items: [
    "**Days 1 and 2:** set up your accounts, create your repository from the starter template and publish a first page on GitHub Pages.",
    "**Day 7:** check in with your site's URL and one paragraph on your plan.",
    "**Day 14:** submit.",
  ] },
  { t: "p", text: "For a one-week case, compress the schedule proportionally." },

  { t: "h1", text: "Getting started" },
  { t: "p", text: "Follow the setup guide. In short:" },
  { t: "ol", items: [
    "Create your repository from the case's starter template, [[" + TEMPLATE_URL + "]]. It already holds the data, the data description sheet, project instructions for your agent, and outlines of your README and agent log.",
    "Turn on GitHub Pages, and publish the starter repository's placeholder page.",
    "Open the repository in your agent. Ask it for a first page that loads the data and shows the number of rows (35,442). Then publish it.",
    "Build in small steps, and check each number before you move on.",
  ] },

  { t: "h1", text: "Citation and license" },
  { t: "p", text: "Cite the dataset on your site and in your README:" },
  { t: "quote", text: CITATION },
  { t: "p", text: LICENSE },
];

const VARIATIONS = [
  { key: "v1", label: "Variation 1: Open Brief", file: "Case Document - Variation 1 (Open Brief).docx", task: TASK_V1 },
  { key: "v2", label: "Variation 2: Specific Questions", file: "Case Document - Variation 2 (Specific Questions).docx", task: TASK_V2 },
  { key: "v3", label: "Variation 3: General Instructions", file: "Case Document - Variation 3 (General Instructions).docx", task: TASK_V3 },
];

// ---------------------------------------------------------------------------
// Setup guide (shared by all variations)
// ---------------------------------------------------------------------------
const SETUP = [
  { t: "p", text: "This guide takes you from a GitHub account to a live website. You will create your repository from the case's starter template, which already holds the data and the files you will fill in. GitHub stores your code and GitHub Pages publishes your site, and both are free for public repositories." },
  { t: "p", text: "It gives no steps for any particular AI coding agent, because agents change quickly. Use your agent's own documentation to install it and open your project folder in it." },

  { t: "h1", text: "What you need" },
  { t: "ul", items: [
    "**A GitHub account.** A free account is enough.",
    "**An AI coding agent** that can read and edit the files in a project folder. Most agents can also run commands, such as starting a local web server or pushing to GitHub. If yours can't, this guide gives another way to do each of those steps.",
    "**A web browser.** A code editor and Git are useful, but your agent may handle what they do.",
    "**The starter template:** [[" + TEMPLATE_URL + "]]. It holds the dataset and the data description sheet, so you don't need to download them.",
  ] },

  { t: "h1", text: "How the pieces fit together" },
  { t: "p", text: "Your project is a folder of plain files: an [[index.html]] page, perhaps CSS and JavaScript files, and a data folder." },
  { t: "ol", items: [
    "Your agent edits the files on your computer.",
    "You preview the site with a local web server and check it.",
    "When the site looks right, you push the files to GitHub.",
    "A workflow in your repository then publishes them with GitHub Pages at [[https://your-username.github.io/your-repo-name/]], usually within a few minutes. The workflow publishes your files as they are. It doesn't build anything.",
  ] },

  { t: "h1", text: "Step 1. Create your repository from the starter template" },
  { t: "ol", items: [
    "Sign in to GitHub and open the starter template at [[" + TEMPLATE_URL + "]].",
    "Click **Use this template**, then **Create a new repository**. Don't use **Fork**: a repository made from the template starts with a clean history, which becomes the record of how your site developed.",
    "Choose your own account as the owner. For a team, one member creates the repository and adds the others under **Settings**, then **Collaborators**.",
    "Give it a short name in lowercase, with hyphens between words, such as [[college-town-site]]. The name becomes part of your site's address.",
    "Make it **Public**. GitHub Pages is free only for public repositories.",
    "Click **Create repository**.",
  ] },
  { t: "p", text: "Your new repository already holds:" },
  { t: "ul", items: [
    "[[data/]]: the dataset in five formats: CSV, Excel, SQLite, DuckDB and Parquet",
    "[[docs/data_description_sheet.md]]: the data description sheet",
    "[[AGENTS.md]]: project instructions for your agent (see Step 4)",
    "[[README.md]] and [[AGENT_LOG.md]]: outlines of two files you will submit",
    "[[scripts/]] and [[checks/]]: folders for scripts that prepare data files, and for your separate checks of the site's numbers",
    "[[index.html]]: a placeholder page",
    "[[.github/workflows/pages.yml]]: the workflow that publishes your site",
  ] },

  { t: "h1", text: "Step 2. Turn on GitHub Pages and publish" },
  { t: "ol", items: [
    "In your repository, open **Settings**, then **Pages**.",
    "Under \"Build and deployment,\" set **Source** to **GitHub Actions**. GitHub may suggest workflows to add. Skip them: your repository already has one.",
    "Open the **Actions** tab, choose **Publish site to GitHub Pages** in the sidebar, click **Run workflow**, then click **Run workflow** again to confirm.",
    "When the run shows a green check, open your site. Its address follows the pattern [[https://your-username.github.io/your-repo-name/]]. For now it shows a placeholder page.",
  ] },
  { t: "p", text: "If the Actions tab already showed a failed run from when you created the repository, that is expected: Pages wasn't turned on yet." },
  { t: "p", text: "From now on, every push to the main branch publishes your site within a few minutes. You can watch each publish in the **Actions** tab." },

  { t: "h1", text: "Step 3. Get the repository onto your computer" },
  { t: "p", text: "Use one of these:" },
  { t: "ul", items: [
    "Ask your agent to clone the repository into a folder on your computer.",
    "Use GitHub Desktop.",
    "Run [[git clone]] yourself.",
  ] },
  { t: "p", text: "Then open that folder in your agent. If your agent runs in the cloud rather than on your computer, connect it to the repository as its documentation describes." },

  { t: "h1", text: "Step 4. Check your agent's project instructions" },
  { t: "p", text: "Many agents read a project instructions file at the start of every session. Your repository's instructions are in [[AGENTS.md]], a name many agents read. Check your agent's documentation: if it expects a different file name, copy [[AGENTS.md]] to that name. If your agent has no such feature, paste the text at the start of each session instead." },
  { t: "p", text: "[[AGENTS.md]] holds this text. Add to it as you learn what your agent needs:" },
  { t: "box", lines: [
    "Project: a data website built from the College-town home sales dataset.",
    "",
    "Rules:",
    "- Use plain HTML, CSS and JavaScript only. No frameworks, no build step, no server-side code. Libraries loaded with a script tag are fine.",
    "- GitHub Pages publishes the site from the repository root. Use relative paths (data/file.csv, not /data/file.csv) and match the exact upper and lower case of file names.",
    "- The data is in data/college_town_home_sales.csv. Read docs/data_description_sheet.md before writing any analysis code, and follow its warnings. Read zipcode, county_fips and parcel_number as text.",
    "- The same data is also in data/ as Excel, SQLite, DuckDB and Parquet files. Never edit any of the five dataset files (data/college_town_home_sales.*). Save any file made from them under a new name, and put the script that makes it in scripts/.",
    "- Never invent or estimate numbers. Compute every number on the site from the data.",
    "- Work in small steps. Before a large change, describe your plan and wait for my approval.",
    "- After each change, tell me what you changed and how I can check it.",
    "- Never put passwords, API keys or other secrets in any file.",
    "- .github/workflows/pages.yml publishes the repository's files to GitHub Pages, as they are, each time main is pushed. Don't add a build step to it.",
  ] },
  { t: "p", text: "**Match upper and lower case exactly** in every file and folder name. GitHub Pages treats [[Data.csv]] and [[data.csv]] as different files, even though your computer may not." },

  { t: "h1", text: "Step 5. Build a first page and preview it" },
  { t: "p", text: "Ask your agent for something like this:" },
  { t: "quote", text: "Replace the placeholder index.html with a page that has a title. Load data/college_town_home_sales.csv and display the number of rows in it. Then start a local web server and tell me the address to open." },
  { t: "p", text: "The page should report **35,442 rows**. If it reports a different number, ask the agent why before you go any further." },
  { t: "p", text: "**Why a local web server?** A browser won't let a page opened straight from a file (an address starting with [[file://]]) load data files. A local web server serves your folder the way GitHub Pages will. If your agent can't run commands, ask it for the command to run yourself." },

  { t: "h1", text: "Step 6. Publish" },
  { t: "ol", items: [
    "Commit your changes and push them to GitHub. You can do this in any of three ways:",
    { sub: [
      "Ask your agent: \"Commit these changes with a short message and push them to GitHub.\"",
      "Use GitHub Desktop.",
      "Upload the changed files on your repository's page on github.com.",
    ] },
    "The push starts the publishing workflow. When its run in the **Actions** tab shows a green check, open your github.io address.",
    "Check the site in a private browser window and on your phone.",
  ] },

  { t: "h1", text: "Step 7. Repeat the build loop" },
  { t: "p", text: "From here on, every change follows the same loop:" },
  { t: "ol", items: [
    "Ask for one small change.",
    "Preview it locally, and check any numbers it changed.",
    "Add an entry to [[AGENT_LOG.md]].",
    "Commit and push. The live site updates within a few minutes.",
  ] },

  { t: "h1", text: "Working well with any agent" },
  { t: "ul", items: [
    "**Start with the data, not the design.** Ask the agent to summarize the dataset and the description sheet's warnings in its own words, and correct anything it gets wrong.",
    "**Ask for a plan before code.** It is easier to fix a plan than a page.",
    "**Make one change at a time.** Small changes are easier to check and to undo.",
    "**Check numbers a second way.** Compute each headline number with a separate method, such as a spreadsheet pivot table, a SQL query on the SQLite file, or a short script in the [[checks]] folder. Record these checks in your README.",
    "**Paste exact errors.** When something breaks, open your browser's developer tools (usually F12, or right-click the page and choose Inspect). Copy the exact error from the Console tab and paste it to your agent.",
    "**Ask why.** If you don't understand the code that computes a number, ask the agent to explain it line by line.",
    "**Save prompts as you go.** Paste your key prompts into [[AGENT_LOG.md]] while you work. They are hard to reconstruct later.",
  ] },

  { t: "h1", text: "Charts, maps and data on a plain HTML site" },
  { t: "ul", items: [
    "**Charts:** load a charting library with a script tag, such as Chart.js, Plotly.js or Apache ECharts. Your agent can also draw charts directly in SVG.",
    "**Maps:** a mapping library such as Leaflet can place sales on a map from their latitude and longitude. Drawing all 35,442 points at once can be slow, so show one town at a time or group nearby points.",
    "**Reading the CSV:** a parsing library such as Papa Parse handles quoted values correctly. Read [[zipcode]], [[county_fips]] and [[parcel_number]] as text, so leading zeros are kept.",
    "**Speed:** the full CSV file is about 9 MB. If your site needs only a few columns or summary figures, prepare a smaller file, such as a JSON summary, and commit the script that created it in the [[scripts]] folder.",
  ] },

  { t: "h1", text: "Common problems" },
  { t: "table", widths: [3000, 3060, 3300], header: ["Problem", "Likely cause", "Fix"], rows: [
    ["The site works locally, but is blank or missing data on GitHub Pages", "A path starts with /, or a file name's capitalization doesn't match", "Use relative paths, and match file names exactly"],
    ["Data won't load when you open index.html directly", "The browser blocks data loading for pages opened from a file", "Preview with a local web server"],
    ["The github.io address shows a 404 page", "Pages isn't turned on, Source isn't set to GitHub Actions, the workflow hasn't run since you turned Pages on, or there is no index.html at the root", "Check Settings, then Pages. Then open the Actions tab, and run the workflow if it hasn't run"],
    ["A run in the Actions tab shows a red X", "The publish failed. Every run fails until Pages is turned on with GitHub Actions as the source", "Open the run and read its error. Check Settings, then Pages, then run the workflow again"],
    ["The live site doesn't show your latest change", "The change wasn't pushed, publishing hasn't finished, or the browser is showing an old copy", "Confirm the push, and wait for a green check in the Actions tab. Then reload without the cache (Ctrl+Shift+R, or Cmd+Shift+R on a Mac)"],
    ["Your numbers differ from the description sheet", "One of the five data problems, such as removing duplicates by address or treating a blank date as zero", "Re-read \"Five things that will bite you,\" and ask the agent to show the code that computes the number"],
  ] },

  { t: "h1", text: "Before you submit" },
  { t: "ul", items: [
    "The repository is public, and the site loads at its github.io address in a private window and on a phone.",
    "No file contains a password, API key or other secret.",
    "The README, the agent log and the reflection are complete, and the README's \"Start here\" section is deleted.",
    "The site cites the dataset.",
    "You have checked the row count and every headline number a second way.",
  ] },
];

module.exports = { TITLE, AUTHOR, FUNDING, CITATION, SHARED_BEFORE, SHARED_AFTER, VARIATIONS, SETUP };
