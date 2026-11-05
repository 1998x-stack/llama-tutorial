/* Dependency-free DOM smoke tests for the 28-chapter static course index. */
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const catalogSource = fs.readFileSync(path.join(root, "courses.js"), "utf8");
const inlineScripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)];
assert.ok(inlineScripts.length > 0, "index.html must contain the index renderer");
assert.match(html, /<script src="courses\.js"><\/script>/);

class Node {
  constructor(tag) {
    this.tagName = tag;
    this.children = [];
    this.attributes = {};
    this.textContent = "";
    this.className = "";
  }
  appendChild(node) {
    this.children.push(node);
    return node;
  }
  replaceChildren(...nodes) {
    this.children = [...nodes];
  }
  setAttribute(key, value) {
    this.attributes[key] = value;
  }
  set innerHTML(value) {
    this.children = [];
    this._html = value;
  }
  get innerHTML() {
    return this._html;
  }
}

function render(withCatalog) {
  const fields = {
    cardContainer: new Node("div"),
    ".header .emoji": new Node("span"),
    ".header .title-text": new Node("span"),
    ".header .sub": new Node("div"),
    ".footer": new Node("div"),
  };
  const document = {
    title: "",
    getElementById: id => fields[id],
    querySelector: selector => fields[selector],
    createElement: tag => new Node(tag),
  };
  const window = {};
  const context = { document, window };
  if (withCatalog) vm.runInNewContext(catalogSource, context, { timeout: 1000 });
  vm.runInNewContext(inlineScripts.at(-1)[1], context, { timeout: 1000 });
  return { document, fields, window };
}

const page = render(true);
const data = JSON.parse(fs.readFileSync(path.join(root, "courses.json"), "utf8"));
const cards = page.fields.cardContainer.children;
assert.equal(cards.length, data.chapterCount);
const anchors = cards.map(card => card.children.at(-1).children[0]);
assert.deepEqual(anchors.map(a => a.href), data.chapters.map(ch => ch.file));
assert.equal(new Set(anchors.map(a => a.textContent)).size, data.chapterCount);
assert.ok(anchors.every(a => a.textContent.includes("开始学习")));
const broken = render(false);
assert.equal(broken.fields.cardContainer.children.length, 1);
assert.equal(broken.fields.cardContainer.children[0].attributes.role, "alert");
assert.match(broken.fields.cardContainer.children[0].textContent, /courses\.js/);

console.log("PASS: 28 course cards, unique links, accessible labels, offline error state");
