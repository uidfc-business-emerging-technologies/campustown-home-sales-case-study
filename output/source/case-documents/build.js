// Builds the Campus Comps case documents and setup guide as editable Word files.
// Usage: node build.js <output-folder>
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  ShadingType, BorderStyle, AlignmentType, LevelFormat, HeadingLevel, Header, Footer,
  PageNumber, TabStopType, LineRuleType,
} = require("docx");
const C = require("./content");

const OUT = process.argv[2] || "out";
const FONT = "Arial";
const MONO = "Consolas";
const BLUE = "13294B";
const GRAY = "5F6B7A";
const RULE = "C9D1DC";
const FILL = "EEF2F7";
const TABLE_W = 9360;

// ---- inline markup: **bold**, [[code]] ------------------------------------
function runs(text, base = {}) {
  const out = [];
  const parts = String(text).split(/(\*\*[^*]+\*\*|\[\[[^\]]+\]\])/);
  for (const part of parts) {
    if (!part) continue;
    if (part.startsWith("**") && part.endsWith("**")) {
      out.push(...runs(part.slice(2, -2), { ...base, bold: true }));
    } else if (part.startsWith("[[") && part.endsWith("]]")) {
      out.push(new TextRun({ text: part.slice(2, -2), font: MONO, size: 20, ...base }));
    } else {
      out.push(new TextRun({ text: part, ...base }));
    }
  }
  return out;
}

// ---- blocks ---------------------------------------------------------------
let listInstance = 0;

function listParas(items, ordered) {
  const ref = ordered ? "numbers" : "bullets";
  const inst = ++listInstance;
  const paras = [];
  for (const item of items) {
    if (typeof item === "object" && item.sub) {
      const subInst = ++listInstance;
      for (const s of item.sub) {
        paras.push(new Paragraph({
          children: runs(s),
          numbering: { reference: ordered ? "numbers" : "bullets", level: 1, instance: ordered ? subInst : inst },
          spacing: { after: 60 },
        }));
      }
    } else {
      paras.push(new Paragraph({
        children: runs(item),
        numbering: { reference: ref, level: 0, instance: inst },
        spacing: { after: 80 },
      }));
    }
  }
  return paras;
}

function tableBlock(b) {
  const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
  const borders = { top: border, bottom: border, left: border, right: border };
  const cell = (text, i, header) => new TableCell({
    width: { size: b.widths[i], type: WidthType.DXA },
    borders,
    shading: header ? { fill: FILL, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: runs(text, header ? { bold: true } : {}), spacing: { after: 0 } })],
  });
  const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: b.header.map((h, i) => cell(h, i, true)) })];
  for (const r of b.rows) rows.push(new TableRow({ cantSplit: true, children: r.map((v, i) => cell(v, i, false)) }));
  return [
    new Table({ width: { size: TABLE_W, type: WidthType.DXA }, columnWidths: b.widths, rows }),
    new Paragraph({ children: [], spacing: { after: 120 } }),
  ];
}

function quoteBlock(text) {
  return [new Paragraph({
    children: runs(text),
    indent: { left: 360, right: 360 },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: BLUE, space: 10 } },
    shading: { fill: FILL, type: ShadingType.CLEAR, color: "auto" },
    spacing: { before: 60, after: 180 },
  })];
}

function boxBlock(lines) {
  const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
  return [
    new Table({
      width: { size: TABLE_W, type: WidthType.DXA },
      columnWidths: [TABLE_W],
      rows: [new TableRow({ cantSplit: true, children: [new TableCell({
        width: { size: TABLE_W, type: WidthType.DXA },
        borders: { top: border, bottom: border, left: border, right: border },
        shading: { fill: FILL, type: ShadingType.CLEAR, color: "auto" },
        margins: { top: 140, bottom: 140, left: 200, right: 200 },
        children: lines.map((l) => new Paragraph({
          children: [new TextRun({ text: l, font: MONO, size: 18 })],
          spacing: { after: 0, line: 240 },
        })),
      })] })],
    }),
    new Paragraph({ children: [], spacing: { after: 120 } }),
  ];
}

function render(blocks) {
  const out = [];
  for (const b of blocks) {
    switch (b.t) {
      case "h1": out.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(b.text)] })); break;
      case "h2": out.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(b.text)] })); break;
      case "p": out.push(new Paragraph({ children: runs(b.text) })); break;
      case "ul": out.push(...listParas(b.items, false)); break;
      case "ol": out.push(...listParas(b.items, true)); break;
      case "table": out.push(...tableBlock(b)); break;
      case "quote": out.push(...quoteBlock(b.text)); break;
      case "box": out.push(...boxBlock(b.lines)); break;
      default: throw new Error("Unknown block " + b.t);
    }
  }
  return out;
}

function titleBlock(subtitle) {
  return [
    new Paragraph({
      children: [new TextRun({ text: C.TITLE, bold: true, size: 40, color: BLUE, font: FONT })],
      spacing: { after: 120 },
    }),
    new Paragraph({
      children: [new TextRun({ text: subtitle, size: 28, color: GRAY, font: FONT })],
      spacing: { after: 120 },
    }),
    new Paragraph({
      children: [new TextRun({ text: C.AUTHOR, size: 22, color: GRAY, font: FONT })],
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 8 } },
      spacing: { after: 240 },
    }),
  ];
}

function makeDoc(headerText, subtitle, blocks) {
  listInstance = 0;
  const body = [...titleBlock(subtitle), ...render(blocks)];
  return new Document({
    creator: "",
    lastModifiedBy: "",
    title: C.TITLE + " - " + subtitle,
    styles: {
      default: { document: { run: { font: FONT, size: 22 }, paragraph: { spacing: { after: 120, line: 276, lineRule: LineRuleType.AUTO } } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 30, bold: true, font: FONT, color: BLUE },
          paragraph: { spacing: { before: 320, after: 120 }, outlineLevel: 0, keepNext: true } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, font: FONT, color: BLUE },
          paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 1, keepNext: true } },
      ],
    },
    numbering: {
      config: [
        { reference: "bullets", levels: [
          { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
        ] },
        { reference: "numbers", levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.LOWER_LETTER, text: "%2.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
        ] },
      ],
    },
    sections: [{
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      headers: { default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: headerText, size: 16, color: GRAY })],
      })] }) },
      footers: { default: new Footer({ children: [new Paragraph({
        tabStops: [{ type: TabStopType.RIGHT, position: 9360 }],
        children: [
          new TextRun({ text: C.FUNDING, size: 16, color: GRAY }),
          new TextRun({ children: ["\tPage ", PageNumber.CURRENT], size: 16, color: GRAY }),
        ],
      })] }) },
      children: body,
    }],
  });
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  for (const v of C.VARIATIONS) {
    const blocks = [...C.SHARED_BEFORE, ...v.task, ...C.SHARED_AFTER];
    const doc = makeDoc("Campus Comps case: " + v.label, v.label, blocks);
    fs.writeFileSync(path.join(OUT, v.file), await Packer.toBuffer(doc));
    console.log("wrote", v.file);
  }
  const setup = makeDoc("Campus Comps case: Setup Guide", "Setup Guide: Building and Publishing Your Site with GitHub Pages", C.SETUP);
  fs.writeFileSync(path.join(OUT, "Setup Guide - GitHub Pages.docx"), await Packer.toBuffer(setup));
  console.log("wrote Setup Guide - GitHub Pages.docx");
}

main().catch((e) => { console.error(e); process.exit(1); });
