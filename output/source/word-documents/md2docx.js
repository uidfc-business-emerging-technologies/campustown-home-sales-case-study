// Converts a markdown file to an editable Word file in the case documents' style.
//
// Supports the markdown these documents use: # to #### headings, paragraphs,
// "-" and "1." lists (one level of nesting), pipe tables, fenced code blocks,
// "> " quotes, "---" rules, images on their own line, and inline **bold**,
// *italic*, `code` and [links](url). A line "<!-- pagebreak -->" starts a new page.
//
// The first "# " heading becomes the title block. Every file gets the funding
// line and page number in its footer, and a blank author.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, AlignmentType, LevelFormat, HeadingLevel, Header, Footer, PageNumber,
  TabStopType, LineRuleType, ExternalHyperlink, ImageRun, PageBreak,
} = require("docx");

const FONT = "Arial";
const MONO = "Consolas";
const BLUE = "13294B";
const LINK = "1F5FAD";
const GRAY = "5F6B7A";
const RULE = "C9D1DC";
const FILL = "EEF2F7";
const TABLE_W = 9360;
const FUNDING = "Funded by the University of Illinois-Deloitte Foundation Center for Business Emerging Technologies.";

// ---- inline markup ---------------------------------------------------------
const INLINE = /(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/;

function runs(text, base = {}) {
  const out = [];
  for (const part of String(text).split(INLINE)) {
    if (!part) continue;
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      out.push(...runs(part.slice(2, -2), { ...base, bold: true }));
    } else if (part.startsWith("`") && part.endsWith("`")) {
      out.push(new TextRun({ text: part.slice(1, -1), font: MONO, size: 20, ...base }));
    } else if (/^\[[^\]]+\]\([^)]+\)$/.test(part)) {
      const [, label, url] = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      out.push(new ExternalHyperlink({
        link: url,
        children: [new TextRun({ text: label, color: LINK, underline: {}, ...base })],
      }));
    } else if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
      out.push(...runs(part.slice(1, -1), { ...base, italics: true }));
    } else {
      out.push(new TextRun({ text: part, ...base }));
    }
  }
  return out;
}

// ---- block parsing ----------------------------------------------------------
function parse(markdown) {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const blocks = [];
  let i = 0;
  const isBlank = (l) => l.trim() === "";
  const isList = (l) => /^\s*(-|\d+\.)\s+/.test(l);
  const startsBlock = (l) => /^(#{1,4} |```|> |\||---\s*$|!\[|<!--)/.test(l) || isList(l);

  while (i < lines.length) {
    const line = lines[i];
    if (isBlank(line)) { i++; continue; }

    let m;
    if ((m = line.match(/^(#{1,4}) (.*)$/))) {
      blocks.push({ t: "h", level: m[1].length, text: m[2].trim() });
      i++;
    } else if (line.startsWith("```")) {
      const code = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) code.push(lines[i++]);
      i++;
      blocks.push({ t: "code", lines: code });
    } else if (line.startsWith("> ") || line === ">") {
      const text = [];
      while (i < lines.length && (lines[i].startsWith("> ") || lines[i] === ">")) text.push(lines[i++].replace(/^> ?/, ""));
      blocks.push({ t: "quote", text: text.join(" ") });
    } else if (line.startsWith("|")) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith("|")) rows.push(lines[i++]);
      blocks.push(parseTable(rows));
    } else if (/^---\s*$/.test(line)) {
      blocks.push({ t: "rule" });
      i++;
    } else if ((m = line.match(/^!\[([^\]]*)\]\(([^)]+)\)\s*$/))) {
      blocks.push({ t: "image", alt: m[1], src: m[2] });
      i++;
    } else if (line.trim() === "<!-- pagebreak -->") {
      blocks.push({ t: "pagebreak" });
      i++;
    } else if (line.startsWith("<!--")) {
      while (i < lines.length && !lines[i].includes("-->")) i++;
      i++;
    } else if (isList(line)) {
      const items = [];
      while (i < lines.length && !isBlank(lines[i]) && (isList(lines[i]) || /^\s{2,}\S/.test(lines[i]))) {
        const l = lines[i];
        const lm = l.match(/^(\s*)(-|\d+\.)\s+(.*)$/);
        if (lm) {
          items.push({ level: lm[1].length >= 2 ? 1 : 0, ordered: lm[2] !== "-", text: lm[3] });
        } else {
          items[items.length - 1].text += " " + l.trim();
        }
        i++;
        // A blank line followed by an indented or list line continues the list.
        if (i < lines.length - 1 && isBlank(lines[i]) && isList(lines[i + 1]) && /^\s/.test(lines[i + 1])) i++;
      }
      blocks.push({ t: "list", items });
    } else {
      const text = [];
      while (i < lines.length && !isBlank(lines[i]) && !(text.length && startsBlock(lines[i]))) text.push(lines[i++].trim());
      blocks.push({ t: "p", text: text.join(" ") });
    }
  }
  return blocks;
}

function splitRow(row) {
  return row.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
}

function parseTable(rows) {
  const header = splitRow(rows[0]);
  const align = splitRow(rows[1]).map((c) => (c.endsWith(":") ? "right" : "left"));
  const body = rows.slice(2).map(splitRow);
  // Each column first gets room for its longest word, so no word breaks; the
  // rest of the width goes to columns in proportion to the text they still need.
  const CHAR = 105; // twips per character at 10 pt, a little wider for code
  const PAD = 240;
  const tokenWidth = (cellText) => Math.max(0, ...cellText.split(/\s+/).map((w) =>
    w.replace(/\*\*|\[|\]\([^)]*\)/g, "").length * (w.includes("`") ? CHAR * 1.2 : CHAR)));
  const textWidth = (cellText) => cellText.replace(/\*\*|`|\[|\]\([^)]*\)/g, "").length * CHAR;
  const columns = header.map((h, c) => [h, ...body.map((r) => r[c] || "")]);
  const minW = columns.map((cells) => Math.max(...cells.map(tokenWidth)) + PAD);
  const wantW = columns.map((cells, c) => Math.max(minW[c], Math.min(Math.max(...cells.map(textWidth)) + PAD, TABLE_W)));
  let widths;
  const minTotal = minW.reduce((a, b) => a + b, 0);
  if (minTotal >= TABLE_W) {
    widths = minW.map((w) => (w / minTotal) * TABLE_W);
  } else {
    const extra = wantW.map((w, c) => w - minW[c]);
    const extraTotal = extra.reduce((a, b) => a + b, 0) || 1;
    widths = minW.map((w, c) => w + (extra[c] / extraTotal) * (TABLE_W - minTotal));
  }
  widths = widths.map(Math.round);
  widths[widths.length - 1] += TABLE_W - widths.reduce((a, b) => a + b, 0);
  return { t: "table", header, align, body, widths };
}

// ---- rendering --------------------------------------------------------------
function pngSize(file) {
  const buf = fs.readFileSync(file);
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20), data: buf };
}

function render(blocks, baseDir) {
  const out = [];
  let listInstance = 0;
  for (const b of blocks) {
    switch (b.t) {
      case "h": {
        const heading = [null, null, HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][b.level];
        out.push(new Paragraph({ heading, children: runs(b.text) }));
        break;
      }
      case "p":
        out.push(new Paragraph({ children: runs(b.text) }));
        break;
      case "list": {
        const top = ++listInstance;
        let sub = null;
        for (const item of b.items) {
          if (item.level === 0) sub = null;
          if (item.level === 1 && sub === null) sub = ++listInstance;
          out.push(new Paragraph({
            children: runs(item.text),
            numbering: {
              reference: item.ordered ? "numbers" : "bullets",
              level: item.level,
              instance: item.level === 0 ? top : sub,
            },
            spacing: { after: item.level === 0 ? 80 : 60 },
          }));
        }
        break;
      }
      case "table": {
        const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
        const borders = { top: border, bottom: border, left: border, right: border };
        const cell = (text, c, header) => new TableCell({
          width: { size: b.widths[c], type: WidthType.DXA },
          borders,
          shading: header ? { fill: FILL, type: ShadingType.CLEAR, color: "auto" } : undefined,
          margins: { top: 60, bottom: 60, left: 100, right: 100 },
          children: [new Paragraph({
            alignment: b.align[c] === "right" ? AlignmentType.RIGHT : AlignmentType.LEFT,
            children: runs(text, header ? { bold: true, size: 20 } : { size: 20 }),
            spacing: { after: 0 },
          })],
        });
        const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: b.header.map((h, c) => cell(h, c, true)) })];
        for (const r of b.body) rows.push(new TableRow({ cantSplit: true, children: b.header.map((_, c) => cell(r[c] || "", c, false)) }));
        out.push(new Table({ width: { size: TABLE_W, type: WidthType.DXA }, columnWidths: b.widths, rows }));
        out.push(new Paragraph({ children: [], spacing: { after: 120 } }));
        break;
      }
      case "code": {
        const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
        out.push(new Table({
          width: { size: TABLE_W, type: WidthType.DXA },
          columnWidths: [TABLE_W],
          rows: [new TableRow({ cantSplit: true, children: [new TableCell({
            width: { size: TABLE_W, type: WidthType.DXA },
            borders: { top: border, bottom: border, left: border, right: border },
            shading: { fill: FILL, type: ShadingType.CLEAR, color: "auto" },
            margins: { top: 120, bottom: 120, left: 160, right: 160 },
            children: b.lines.map((l) => new Paragraph({
              children: [new TextRun({ text: l, font: MONO, size: 17 })],
              spacing: { after: 0, line: 240 },
            })),
          })] })],
        }));
        out.push(new Paragraph({ children: [], spacing: { after: 120 } }));
        break;
      }
      case "quote":
        out.push(new Paragraph({
          children: runs(b.text),
          indent: { left: 360, right: 360 },
          border: { left: { style: BorderStyle.SINGLE, size: 18, color: BLUE, space: 10 } },
          shading: { fill: FILL, type: ShadingType.CLEAR, color: "auto" },
          spacing: { before: 60, after: 180 },
        }));
        break;
      case "rule":
        out.push(new Paragraph({ children: [], border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 4 } }, spacing: { after: 160 } }));
        break;
      case "image": {
        const img = pngSize(path.resolve(baseDir, b.src));
        const width = Math.min(600, img.width);
        out.push(new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new ImageRun({
            type: "png",
            data: img.data,
            transformation: { width, height: Math.round((img.height * width) / img.width) },
            altText: { title: b.alt, description: b.alt, name: path.basename(b.src) },
          })],
          spacing: { after: 160 },
        }));
        break;
      }
      case "pagebreak":
        out.push(new Paragraph({ children: [new PageBreak()] }));
        break;
      default:
        throw new Error("Unknown block " + b.t);
    }
  }
  return out;
}

function titleBlock(title, subtitle, author) {
  const out = [new Paragraph({ children: [new TextRun({ text: title, bold: true, size: 40, color: BLUE, font: FONT })], spacing: { after: 120 } })];
  if (subtitle) out.push(new Paragraph({ children: [new TextRun({ text: subtitle, size: 28, color: GRAY, font: FONT })], spacing: { after: 120 } }));
  out.push(new Paragraph({
    children: author ? [new TextRun({ text: author, size: 22, color: GRAY, font: FONT })] : [],
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 8 } },
    spacing: { after: 240 },
  }));
  return out;
}

async function convert({ source, output, header, subtitle, author }) {
  const blocks = parse(fs.readFileSync(source, "utf8"));
  const first = blocks.findIndex((b) => b.t === "h" && b.level === 1);
  if (first < 0) throw new Error(source + " has no # title");
  const title = blocks[first].text;
  blocks.splice(first, 1);

  const doc = new Document({
    creator: "",
    lastModifiedBy: "",
    title: subtitle ? title + " - " + subtitle : title,
    styles: {
      default: { document: { run: { font: FONT, size: 22 }, paragraph: { spacing: { after: 120, line: 276, lineRule: LineRuleType.AUTO } } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 30, bold: true, font: FONT, color: BLUE },
          paragraph: { spacing: { before: 320, after: 120 }, outlineLevel: 0, keepNext: true } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, font: FONT, color: BLUE },
          paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 1, keepNext: true } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 22, bold: true, font: FONT, color: BLUE },
          paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2, keepNext: true } },
      ],
    },
    numbering: {
      config: [
        { reference: "bullets", levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
        ] },
        { reference: "numbers", levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.LOWER_LETTER, text: "%2.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
        ] },
      ],
    },
    sections: [{
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: header, size: 16, color: GRAY })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({
        tabStops: [{ type: TabStopType.RIGHT, position: 9360 }],
        children: [
          new TextRun({ text: FUNDING, size: 16, color: GRAY }),
          new TextRun({ children: ["\tPage ", PageNumber.CURRENT], size: 16, color: GRAY }),
        ],
      })] }) },
      children: [...titleBlock(title, subtitle, author), ...render(blocks, path.dirname(source))],
    }],
  });
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, await Packer.toBuffer(doc));
}

module.exports = { convert, parse };
