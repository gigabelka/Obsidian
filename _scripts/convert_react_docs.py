#!/usr/bin/env python3
"""Convert react.dev MDX documentation into clean Markdown for an Obsidian vault.

Source:  c:/Temp/react.dev-main (src/content, public/images)
Target:  <vault>/React

Conversion rules:
- Strips MDX component tags, keeping their text content.
- Note/Pitfall/DeepDive/Hint/Wip become Obsidian callouts (> [!type]).
- Sandpack blocks become plain fenced code blocks, one per file, each
  preceded by a bold file name.
- Diagram/Illustration components become image links (images are copied).
- Internal links (/learn/..., /reference/...) become relative .md links;
  links to sections not included in the vault become absolute react.dev URLs.
- Generates React/INDEX.md from the sidebar JSON files.
"""

import json
import os
import re
import shutil
import sys
import time

SRC = os.environ.get("REACT_SRC", r"c:\Temp\react.dev-main")
CONTENT = os.path.join(SRC, "src", "content")
PUBLIC = os.path.join(SRC, "public")
DST = os.environ.get("REACT_DST", r"c:\Yandex.Disk\Obsidian\Docs\React")

SECTIONS = ["learn", "reference", "errors", "warnings"]
SKIP_FILES = {"learn/rsc-sandbox-test.md"}
SITE = "https://react.dev"

# ---------------------------------------------------------------- file map --

def collect_files():
    """url path (without extension) -> content-relative path"""
    files = {}
    for sec in SECTIONS:
        base = os.path.join(CONTENT, sec)
        for root, _dirs, names in os.walk(base):
            for name in names:
                if not name.endswith(".md"):
                    continue
                full = os.path.join(root, name)
                rel = os.path.relpath(full, CONTENT).replace("\\", "/")
                if rel in SKIP_FILES:
                    continue
                url = "/" + rel[:-3]
                files[url] = rel
                if url.endswith("/index"):
                    files[url[:-6]] = rel  # /learn/index -> /learn
    return files

# ------------------------------------------------------------- conversion --

CALLOUTS = {
    "Note": ("note", ""),
    "Pitfall": ("warning", "Pitfall"),
    "DeepDive": ("info", "Deep Dive"),
    "Hint": ("tip", "Hint"),
    "Wip": ("warning", "Work in progress"),
}
FENCE_BLOCKS = {
    "TerminalBlock": "bash",
    "ConsoleBlock": "text",
    "ConsoleBlockMulti": "text",
    "ShowRenderedHTML": "html",
}
# Block tags that are simply removed (content kept as-is).
STRIP_BLOCKS = {
    "Intro", "YouWillLearn", "Challenges", "Recap", "DiagramGroup",
    "IllustrationBlock", "Sandpack", "SandpackRSC", "SandpackWithHTMLOutput",
    "Section", "RSC", "Details", "Expandable", "Math", "MathI", "Recipes",
    "Recipe", "TableOfContents", "ErrorBoundary", "ErrorDecoder",
    "Playground", "Preview", "Editor", "TestCase", "TestComponent",
}
# Tags removed together with everything until the matching close tag.
DROP_BLOCKS = {"InlineToc", "VideoPlaceholder", "TeamMember", "Author"}
BADGES = {
    "CanaryBadge": "(Canary)",
    "ExperimentalBadge": "(Experimental)",
    "DeprecatedBadge": "(Deprecated)",
}

ATTR_RE = re.compile(r"(\w+)=(?:\"([^\"]*)\"|'([^']*)')")
_ATTR = r"(?:\s+[\w]+(?:=\{[^}]*\}|=\"[^\"]*\"|='[^']*')?)*"
OPEN_TAG_RE = re.compile(r"^<([A-Z][A-Za-z]*)(" + _ATTR + r")\s*(/?)>$")
CLOSE_TAG_RE = re.compile(r"^</([A-Z][A-Za-z]*)>$")
INLINE_TAG_RE = re.compile(r"</?[A-Z][A-Za-z]*(?:" + _ATTR + r")\s*/?>")
INLINE_CODE_SPLIT_RE = re.compile(r"(`+[^`]*`+)")
MDX_COMMENT_RE = re.compile(r"\{/\*.*?\*/\}")
LINK_RE = re.compile(r"\]\((/[^)\s]*)\)")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(```+|~~~+)(.*)$")


def parse_attrs(text):
    return {m.group(1): m.group(2) if m.group(2) is not None else m.group(3)
            for m in ATTR_RE.finditer(text)}


class Converter:
    def __init__(self, url_map, out_rel):
        self.url_map = url_map          # url path -> content-relative path
        self.out_rel = out_rel          # output-relative path of current file
        self.images = {}                # source abs path -> vault-relative path
        self.lines = []
        self.fence = None               # active fence marker or None
        self.callout_stack = []
        self.drop_until = None          # tag name whose close we await
        self.diagram = None             # dict while inside <Diagram>...</Diagram>
        self.learnmore = None           # dict while inside <LearnMore>...</LearnMore>
        self.pending_fence_lang = None  # lang for </TerminalBlock>-opened fence
        self.heading_anchors = {}       # custom {/*slug*/} -> heading text

    # -- helpers ----------------------------------------------------------

    def emit(self, text=""):
        prefix = "> " * len(self.callout_stack)
        if prefix and text:
            self.lines.append(prefix + text)
        elif prefix:
            self.lines.append(prefix.rstrip())
        else:
            self.lines.append(text)

    def rel_link(self, target_rel):
        """Relative path from current output file to another output .md file."""
        src_dir = os.path.dirname(self.out_rel)
        return os.path.relpath(target_rel, src_dir).replace("\\", "/")

    def resolve_url(self, url):
        path, _, anchor = url.partition("#")
        path = path.rstrip("/") or "/"
        suffix = ("#" + anchor) if anchor else ""
        if path in self.url_map:
            return self.rel_link(self.url_map[path]) + suffix
        if path + "/index" in self.url_map:
            return self.rel_link(self.url_map[path + "/index"]) + suffix
        return SITE + path + suffix

    def register_image(self, src):
        """Map an image reference to a copied vault image; return vault-relative path."""
        if src.startswith("http"):
            return src
        if src.startswith("/"):
            abs_src = os.path.join(PUBLIC, src.lstrip("/").replace("/", os.sep))
            sub = src.lstrip("/")
        else:
            # relative to the current source file's directory
            src_content = self.url_map[self.self_url]
            abs_src = os.path.normpath(os.path.join(CONTENT, os.path.dirname(src_content), src))
            sub = os.path.relpath(abs_src, CONTENT).replace("\\", "/")
            # some relative links (e.g. ../images/tutorial/...) actually
            # resolve into public/images on the site
            if not os.path.isfile(abs_src) and sub.startswith("images/"):
                alt_src = os.path.join(PUBLIC, sub.replace("/", os.sep))
                if os.path.isfile(alt_src):
                    abs_src = alt_src
        if abs_src not in self.images:
            self.images[abs_src] = sub
        vault_path = "images/" + sub[len("images/"):] if sub.startswith("images/") else "images/" + sub
        self.images[abs_src] = vault_path
        src_dir = os.path.dirname(self.out_rel)
        return os.path.relpath(vault_path, src_dir).replace("\\", "/")

    def rewrite_inline(self, text):
        # process inline code spans separately so `<Section>` inside
        # backticks is preserved
        parts = INLINE_CODE_SPLIT_RE.split(text)
        return "".join(
            part if part.startswith("`") else self._rewrite_text(part)
            for part in parts
        )

    def _rewrite_text(self, text):
        # MDX comments ({/* ... */})
        text = MDX_COMMENT_RE.sub("", text)
        # badges -> plain-text markers
        for badge, label in BADGES.items():
            text = re.sub(r"<" + badge + r"\s*/>", label + " ", text)
        # strip any remaining inline component tags
        text = INLINE_TAG_RE.sub("", text)
        # links
        text = LINK_RE.sub(lambda m: "](" + self.resolve_url(m.group(1)) + ")", text)
        # images
        def img_sub(m):
            alt, src = m.group(1), m.group(2)
            if src.startswith("http"):
                return m.group(0)
            return "![%s](%s)" % (alt, self.register_image(src))
        text = IMG_RE.sub(img_sub, text)
        return text

    # -- main loop ---------------------------------------------------------

    def convert(self, body, self_url):
        self.self_url = self_url
        for raw in body.split("\n"):
            line = raw.rstrip()
            self.process_line(line)
        out = "\n".join(self.lines)
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out.strip() + "\n"

    def process_line(self, line):
        # inside a fenced code block: pass through untouched
        fence_m = FENCE_RE.match(line)
        if self.fence:
            self.emit(line)
            if fence_m and fence_m.group(1).startswith(self.fence[0]) and not fence_m.group(2).strip():
                self.fence = None
            return

        if self.drop_until:
            close = CLOSE_TAG_RE.match(line)
            if close and close.group(1) == self.drop_until:
                self.drop_until = None
            return

        # inside <Diagram>...</Diagram>: capture caption
        if self.diagram is not None:
            close = CLOSE_TAG_RE.match(line)
            if close and close.group(1) == "Diagram":
                self.emit_diagram()
            elif line.strip():
                self.diagram["caption"] += line.strip() + " "
            return

        # inside <LearnMore>...</LearnMore>: capture text
        if self.learnmore is not None:
            close = CLOSE_TAG_RE.match(line)
            if close and close.group(1) == "LearnMore":
                # inner content already links to the page; emit it as-is
                self.emit()
                for para in self.learnmore["paras"]:
                    self.emit(para)
                    self.emit()
                self.learnmore = None
            else:
                if line.strip():
                    self.learnmore["paras"].append(self.rewrite_inline(line).strip())
            return

        # fence opening (possibly with Sandpack file-name info string)
        if fence_m:
            marker, info = fence_m.group(1), fence_m.group(2).strip()
            self.open_fence(marker, info)
            return

        stripped = line.strip()
        open_m = OPEN_TAG_RE.match(stripped)
        close_m = CLOSE_TAG_RE.match(stripped)

        if open_m:
            self.handle_open(open_m.group(1), open_m.group(2), open_m.group(3) == "/")
            return
        if close_m:
            self.handle_close(close_m.group(1))
            return

        # remember custom heading anchors ({/*slug*/}) before stripping them
        heading_m = re.match(r"^(#{1,6}\s+)(.*?)\s*\{/\*([\w-]+)\*/\}\s*$", line)
        if heading_m:
            title = heading_m.group(2).strip()
            self.heading_anchors[heading_m.group(3)] = title
            self.emit(heading_m.group(1) + title)
            return

        self.emit(self.rewrite_inline(line))

    def open_fence(self, marker, info):
        """Normalize fence info strings: keep language, lift file name out."""
        self.fence = marker
        tokens = info.split()
        lang, filename = "", None
        if tokens and re.fullmatch(r"[A-Za-z0-9#+.-]+", tokens[0]):
            lang = tokens[0]
            tokens = tokens[1:]
        for tok in tokens:
            if ("/" in tok or "." in tok) and re.fullmatch(r"[\w./-]+", tok):
                filename = tok
                break
        if filename:
            self.emit()
            self.emit("**%s**" % filename)
            self.emit()
        self.emit(marker + lang)

    def handle_open(self, tag, attrs_text, self_closing):
        attrs = parse_attrs(attrs_text)
        if tag in CALLOUTS:
            kind, label = CALLOUTS[tag]
            self.emit()
            self.emit("> [!%s]%s" % (kind, (" " + label) if label else ""))
            self.callout_stack.append(tag)
        elif tag in FENCE_BLOCKS:
            self.emit()
            self.emit("```" + FENCE_BLOCKS[tag])
            self.pending_fence_lang = tag
        elif tag == "Solution":
            self.emit()
            self.emit("**Solution:**")
            self.emit()
        elif tag == "Diagram":
            self.diagram = {"name": attrs.get("name", ""), "alt": attrs.get("alt", ""), "caption": ""}
            if self_closing:
                self.emit_diagram()
        elif tag == "Illustration":
            src = attrs.get("src", "")
            alt = attrs.get("alt", "")
            caption = attrs.get("caption", "")
            self.emit()
            if src:
                self.emit("![%s](%s)" % (alt, self.register_image(src)))
            if caption:
                self.emit()
                self.emit("*%s*" % caption)
            self.emit()
        elif tag == "LearnMore":
            self.learnmore = {"path": attrs.get("path", "/"), "paras": []}
        elif tag == "Recipes" and "titleText" in attrs:
            title = attrs["titleText"]
            self.emit()
            self.emit("## " + title)
            self.emit()
            if "titleId" in attrs:
                self.heading_anchors[attrs["titleId"]] = title
        elif tag in DROP_BLOCKS:
            if not self_closing:
                self.drop_until = tag
        elif tag in BADGES:
            self.emit(BADGES[tag])
        elif tag in STRIP_BLOCKS:
            pass
        else:
            # unknown component: drop the tag, keep following content
            pass

    def handle_close(self, tag):
        if tag in CALLOUTS:
            if self.callout_stack and self.callout_stack[-1] == tag:
                self.callout_stack.pop()
            self.emit()
        elif tag in FENCE_BLOCKS:
            self.emit("```")
            self.emit()
            self.pending_fence_lang = None
        elif tag in STRIP_BLOCKS or tag == "Solution":
            pass
        # unknown close tags: drop

    def emit_diagram(self):
        d = self.diagram
        self.diagram = None
        self.emit()
        if d["name"]:
            src = "/images/docs/diagrams/%s.png" % d["name"]
            self.emit("![%s](%s)" % (d["alt"], self.register_image(src)))
        elif d["alt"]:
            self.emit("*%s*" % d["alt"])
        caption = d["caption"].strip()
        if caption:
            self.emit()
            self.emit("*%s*" % caption)
        self.emit()


def split_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end]
            body = text[end + 4:]
            # title key, or a single arbitrary key used as the page title
            # (e.g. reference pages use `link: "<link>"` as frontmatter)
            m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', fm, re.M)
            if not m:
                m = re.search(r'^\w+:\s*["\']?(.*?)["\']?\s*$', fm, re.M)
            title = m.group(1) if m else None
            return title, body.lstrip("\n")
    return None, text


# --------------------------------------------------------- anchor fixing --

def github_slug(text):
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def extract_headings(text):
    """slug -> original heading text for every heading in a markdown file"""
    headings = {}
    fence = None
    for line in text.split("\n"):
        m = FENCE_RE.match(line)
        if m:
            if fence is None:
                fence = m.group(1)
            elif m.group(1).startswith(fence[0]) and not m.group(2).strip():
                fence = None
            continue
        if fence:
            continue
        h = re.match(r"^#{1,6}\s+(.*)$", line)
        if h:
            title = h.group(1).strip()
            slug = github_slug(title)
            headings.setdefault(slug, title)
    return headings


ANCHOR_LINK_RE = re.compile(r"\]\(([^)#\s]+\.md)?#([^)\s]+)\)")


def fix_anchor_links(path, heading_maps):
    """Rewrite #anchor links (GitHub slugs) to Obsidian format (#Heading text)."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    rel = os.path.relpath(path, DST).replace("\\", "/")
    src_dir = os.path.dirname(rel)

    def sub(m):
        target, anchor = m.group(1), m.group(2)
        if target and target.startswith(("http://", "https://")):
            return m.group(0)
        if target:
            target_abs = os.path.normpath(os.path.join(src_dir, target)).replace("\\", "/")
        else:
            target_abs = rel
        headings = heading_maps.get(target_abs)
        if not headings:
            return m.group(0)
        heading = headings.get(anchor)
        if heading is None:
            heading = headings.get(anchor.lower())
        if heading is None:
            return m.group(0)
        # parentheses would break the markdown link destination; encode them
        heading = heading.replace("(", "%28").replace(")", "%29")
        prefix = target or ""
        return "](%s#%s)" % (prefix, heading)

    fixed = ANCHOR_LINK_RE.sub(sub, text)
    if fixed != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(fixed)

# ------------------------------------------------------------------- main --

def main():
    url_map = collect_files()
    os.makedirs(DST, exist_ok=True)

    all_images = {}
    custom_anchors = {}
    written = {}  # content rel -> title
    for url, rel in sorted(url_map.items(), key=lambda kv: kv[1]):
        if rel in written:
            continue
        with open(os.path.join(CONTENT, rel), encoding="utf-8") as f:
            text = f.read()
        title, body = split_frontmatter(text)
        conv = Converter(url_map, rel)
        converted = conv.convert(body, url)
        if not title:
            # errors/ and similar files have no frontmatter; use the file name
            stem = os.path.basename(rel)[:-3]
            title = "Error %s" % stem if stem.isdigit() else stem.replace("-", " ").title()
            if stem == "index":
                title = rel.split("/")[0].replace("-", " ").title()
        converted = "# %s\n\n%s" % (title, converted)
        out_path = os.path.join(DST, rel)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(converted)
        written[rel] = title
        all_images.update(conv.images)
        if conv.heading_anchors:
            custom_anchors[rel] = conv.heading_anchors

    # copy images
    copied, missing = 0, 0
    for abs_src, vault_rel in sorted(all_images.items()):
        dst = os.path.join(DST, vault_rel.replace("/", os.sep))
        if os.path.isfile(abs_src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(abs_src, dst)
            copied += 1
        else:
            missing += 1
            print("MISSING IMAGE: %s" % abs_src, file=sys.stderr)

    generate_index(written)
    fix_all_anchors(custom_anchors)
    print("Converted %d files, copied %d images (%d missing)." % (len(written), copied, missing))


def fix_all_anchors(custom_anchors):
    heading_maps = {}
    for root, _dirs, names in os.walk(DST):
        for name in names:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, DST).replace("\\", "/")
            with open(path, encoding="utf-8") as f:
                heading_maps[rel] = extract_headings(f.read())
    # merge in the original {/*custom*/} anchors captured during conversion
    for rel, anchors in custom_anchors.items():
        heading_maps.setdefault(rel, {}).update(anchors)
    fixed = 0
    for root, _dirs, names in os.walk(DST):
        for name in names:
            if name.endswith(".md"):
                before = None
                path = os.path.join(root, name)
                with open(path, encoding="utf-8") as f:
                    before = f.read()
                fix_anchor_links(path, heading_maps)
                with open(path, encoding="utf-8") as f:
                    if f.read() != before:
                        fixed += 1
    print("Fixed anchor links in %d files." % fixed)


def generate_index(titles):
    lines = ["# React Documentation Index", ""]
    lines.append("Source: [react.dev](%s) (offline snapshot)." % SITE)
    lines.append("")
    for sidebar_file, heading in [
        ("sidebarLearn.json", "Learn React"),
        ("sidebarReference.json", "API Reference"),
    ]:
        with open(os.path.join(SRC, "src", sidebar_file), encoding="utf-8") as f:
            sidebar = json.load(f)
        lines.append("## %s" % heading)
        lines.append("")
        walk_routes(sidebar.get("routes", []), lines, 0)
        lines.append("")

    lines.append("## Errors and Warnings")
    lines.append("")
    err_files = sorted(
        (rel for rel in titles if rel.startswith(("errors/", "warnings/"))),
        key=lambda r: (r.split("/")[0], "index" not in r, r),
    )
    for rel in err_files:
        title = titles[rel] or os.path.basename(rel)[:-3]
        if rel.endswith("/index.md"):
            title = {"errors": "Errors Overview", "warnings": "Warnings Overview"}.get(rel.split("/")[0], title)
        lines.append("- [%s](%s)" % (title, rel))
    lines.append("")

    with open(os.path.join(DST, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def walk_routes(routes, lines, depth):
    for route in routes:
        if route.get("hasSectionHeader"):
            lines.append("")
            lines.append("%s**%s**" % ("  " * depth, route["sectionHeader"].replace("{{version}}", "latest")))
            continue
        title = route.get("title", "")
        path = route.get("path", "")
        if path:
            rel = path.lstrip("/") + ".md"
            if not os.path.isfile(os.path.join(DST, rel.replace("/", os.sep))):
                rel = path.lstrip("/") + "/index.md"
            if os.path.isfile(os.path.join(DST, rel.replace("/", os.sep))):
                lines.append("%s- [%s](%s)" % ("  " * depth, title, rel))
            else:
                lines.append("%s- %s" % ("  " * depth, title))
        else:
            lines.append("%s- **%s**" % ("  " * depth, title))
        if route.get("routes"):
            walk_routes(route["routes"], lines, depth + 1)


if __name__ == "__main__":
    main()
