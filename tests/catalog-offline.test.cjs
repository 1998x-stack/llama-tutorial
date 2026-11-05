"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const asset = fs.readFileSync(path.join(root, "courses-data.js"), "utf8");
const catalog = JSON.parse(fs.readFileSync(path.join(root, "courses.json"), "utf8"));
const script = html.match(/<script>\s*([\s\S]*?)<\/script>/i);
assert.ok(script, "index.html must include its catalog-rendering script");

class Element {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this.className = "";
    this.href = "";
    this._text = "";
  }
  set textContent(value) {
    this._text = String(value);
    this.children = [];
  }
  get textContent() {
    return this._text + this.children.map((item) => item.textContent).join("");
  }
  appendChild(element) {
    this.children.push(element);
    return element;
  }
  replaceChildren(...elements) {
    this._text = "";
    this.children = elements;
  }
}

async function render(data) {
  const container = new Element("div");
  const title = new Element("span");
  const selectors = {
    ".header .emoji": new Element("span"),
    ".header .title-text": title,
    ".header .sub": new Element("div"),
    ".footer": new Element("div"),
  };
  const document = {
    title: "",
    getElementById: (id) => {
      assert.equal(id, "cardContainer");
      return container;
    },
    querySelector: (selector) => selectors[selector],
    createElement: (tag) => new Element(tag),
    createTextNode: (value) => ({ textContent: String(value) }),
  };
  let fetchCount = 0;
  const window = { LLAMA_COURSES: data };
  vm.runInNewContext(script[1], {
    document,
    window,
    fetch() {
      fetchCount++;
      throw new Error("file:// must not require fetch()");
    },
  });
  await new Promise((resolve) => setImmediate(resolve));
  return { document, container, title, fetchCount };
}

test("offline JS manifest exactly matches the canonical JSON", () => {
  const window = {};
  vm.runInNewContext(asset, { window });
  assert.deepEqual(JSON.parse(JSON.stringify(window.LLAMA_COURSES)), catalog);
  assert.match(html, /<script src="courses-data\.js"><\/script>/);
  assert.doesNotMatch(html, /fetch\s*\(\s*["']courses\.json["']/);
});

test("all local chapter files are safe and exist", () => {
  assert.equal(catalog.chapterCount, catalog.chapters.length);
  assert.equal(catalog.chapters.length, 28);
  const seen = new Set();
  for (const chapter of catalog.chapters) {
    assert.match(chapter.file, /^[0-9]{2}\.html$/);
    assert.equal(chapter.num + ".html", chapter.file);
    assert.equal(seen.has(chapter.file), false);
    assert.ok(fs.statSync(path.join(root, chapter.file)).isFile());
    seen.add(chapter.file);
  }
});

test("catalog renders 28 navigable cards without fetch", async () => {
  const result = await render(catalog);
  assert.equal(result.fetchCount, 0);
  const cards = result.container.children;
  assert.equal(cards.length, 28);
  assert.match(result.document.title, /课程目录/);
  const firstLink = cards[0].children.find((x) => x.className === "card-footer").children[0];
  assert.equal(firstLink.href, "01.html");
  const lastLink = cards.at(-1).children.find((x) => x.className === "card-footer").children[0];
  assert.equal(lastLink.href, "28.html");
});

test("rejects invalid chapter URLs and displays text-only errors", async () => {
  const malformed = {
    ...catalog,
    chapters: [{ num: "01", title: "坏链接", topics: [], file: "javascript:alert(1)" }],
  };
  const { container, fetchCount } = await render(malformed);
  assert.equal(fetchCount, 0);
  assert.equal(container.children[0].className, "state-msg error");
  assert.match(container.children[0].textContent, /课程文件路径无效/);
});
