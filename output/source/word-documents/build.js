// Builds every Word document that is not a case document, from its markdown source.
// Usage, from this folder, with the docx npm package installed:
//   node build.js
// Paths are relative to the output/ folder.
const path = require("path");
const { convert } = require("./md2docx");

const OUTPUT = path.resolve(__dirname, "..", "..");
const TITLE = "Campus Comps: Building a Data Website with an AI Coding Agent";
const AUTHOR = "[Author name]";

const DOCUMENTS = [
  {
    source: "students/data_description_sheet.md",
    output: "students/Data Description Sheet.docx",
    header: "College-town home sales dataset: Data description sheet",
    subtitle: "Version 1.0",
  },
];

async function main() {
  for (const d of DOCUMENTS) {
    await convert({
      ...d,
      source: path.join(OUTPUT, d.source),
      output: path.join(OUTPUT, d.output),
    });
    console.log("wrote", d.output);
  }
}

module.exports = { TITLE, AUTHOR };
if (require.main === module) main().catch((e) => { console.error(e); process.exit(1); });
