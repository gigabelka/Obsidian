#!/usr/bin/env python3
"""Convert typescriptlang.org documentation into clean Markdown for an Obsidian vault.

Source:  c:/Temp/TypeScript-Website-2 (packages/documentation/copy/en,
         packages/tsconfig-reference/copy/en, packages/typescriptlang-org/static)
Target:  <vault>/Docs/TypeScript

Conversion rules:
- Frontmatter is stripped; `title` (or `display`) becomes the page's H1.
- Twoslash code blocks (```ts twoslash) are cleaned: the flag is removed,
  `// @directive` lines and `^?` hover markers are stripped, and multi-file
  samples (`// @filename: x.ts`) are split into separate fenced blocks, each
  preceded by a bold file name (Sandpack style, like the React docs).
- Internal links (/docs/handbook/...html) become relative .md links via the
  permalink map built from frontmatter; /tsconfig#option links point to the
  converted option pages; everything else becomes an absolute
  typescriptlang.org URL. Deprecated handbook-v1 permalinks redirect to the
  corresponding v2 pages.
- Images under /images/ are copied into TypeScript/images/; modules-reference
  SVG diagrams are copied next to their pages. External hotlinks are kept.
- Output file names are slugified to kebab-case.
- Generates TypeScript/INDEX.md following the site's documentation
  navigation (generateDocsNavigationPerLanguage.js).
"""

import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convert_react_docs import FENCE_RE, extract_headings, github_slug

SRC = os.environ.get("TS_SRC", r"c:\Temp\TypeScript-Website-2")
DOCS = os.path.join(SRC, "packages", "documentation", "copy", "en")
TSCONFIG = os.path.join(SRC, "packages", "tsconfig-reference", "copy", "en")
STATIC = os.path.join(SRC, "packages", "typescriptlang-org", "static")
DST = os.environ.get("TS_DST", r"c:\Yandex.Disk\Obsidian\Docs\TypeScript")

SITE = "https://www.typescriptlang.org"

# ------------------------------------------------------------- static data --

# tsconfig option name -> category code, dumped from the TypeScript 5.9
# compiler's optionDeclarations (option.category.code). Options absent from
# the compiler table (top-level tsconfig fields, watch/typeAcquisition/CLI
# extras) are listed in EXTRA_CATEGORY below.
OPTION_CATEGORY = {
    "preserveWatchOutput": 6256, "pretty": 6256, "noErrorTruncation": 6256,
    "listFiles": 6251, "explainFiles": 6251, "listEmittedFiles": 6251,
    "traceResolution": 6251, "diagnostics": 6251, "extendedDiagnostics": 6251,
    "generateCpuProfile": 6251, "generateTrace": 6251, "noCheck": 6251,
    "incremental": 6255, "composite": 6255, "tsBuildInfoFile": 6255,
    "disableSourceOfProjectReferenceRedirect": 6255,
    "disableSolutionSearching": 6255, "disableReferencedProjectLoad": 6255,
    "declaration": 6246, "declarationMap": 6246, "emitDeclarationOnly": 6246,
    "sourceMap": 6246, "inlineSourceMap": 6246, "noEmit": 6246,
    "outFile": 6246, "outDir": 6246, "removeComments": 6246,
    "importHelpers": 6246, "downlevelIteration": 6246, "sourceRoot": 6246,
    "mapRoot": 6246, "inlineSources": 6246, "emitBOM": 6246, "newLine": 6246,
    "stripInternal": 6246, "noEmitHelpers": 6246, "noEmitOnError": 6246,
    "preserveConstEnums": 6246, "declarationDir": 6246,
    "assumeChangesOnlyAffectDirectDependencies": 6250,
    "target": 6254, "lib": 6254, "jsx": 6254, "libReplacement": 6254,
    "experimentalDecorators": 6254, "emitDecoratorMetadata": 6254,
    "jsxFactory": 6254, "jsxFragmentFactory": 6254, "jsxImportSource": 6254,
    "reactNamespace": 6254, "noLib": 6254, "moduleDetection": 6254,
    "useDefineForClassFields": 6254,
    "module": 6244, "rootDir": 6244, "moduleResolution": 6244, "baseUrl": 6244,
    "paths": 6244, "rootDirs": 6244, "typeRoots": 6244, "types": 6244,
    "allowUmdGlobalAccess": 6244, "moduleSuffixes": 6244,
    "allowImportingTsExtensions": 6244, "rewriteRelativeImportExtensions": 6244,
    "resolvePackageJsonExports": 6244, "resolvePackageJsonImports": 6244,
    "customConditions": 6244, "noUncheckedSideEffectImports": 6244,
    "resolveJsonModule": 6244, "allowArbitraryExtensions": 6244,
    "noResolve": 6244,
    "allowJs": 6247, "checkJs": 6247, "maxNodeModuleJsDepth": 6247,
    "isolatedModules": 6252, "verbatimModuleSyntax": 6252,
    "isolatedDeclarations": 6252, "erasableSyntaxOnly": 6252,
    "allowSyntheticDefaultImports": 6252, "esModuleInterop": 6252,
    "preserveSymlinks": 6252, "forceConsistentCasingInFileNames": 6252,
    "importsNotUsedAsValues": 6253, "charset": 6253, "out": 6253,
    "noImplicitUseStrict": 6253, "suppressExcessPropertyErrors": 6253,
    "suppressImplicitAnyIndexErrors": 6253, "noStrictGenericChecks": 6253,
    "preserveValueImports": 6253, "keyofStringsOnly": 6253,
    "strict": 6248, "noImplicitAny": 6248, "strictNullChecks": 6248,
    "strictFunctionTypes": 6248, "strictBindCallApply": 6248,
    "strictPropertyInitialization": 6248, "strictBuiltinIteratorReturn": 6248,
    "noImplicitThis": 6248, "useUnknownInCatchVariables": 6248,
    "alwaysStrict": 6248, "noUnusedLocals": 6248, "noUnusedParameters": 6248,
    "exactOptionalPropertyTypes": 6248, "noImplicitReturns": 6248,
    "noFallthroughCasesInSwitch": 6248, "noUncheckedIndexedAccess": 6248,
    "noImplicitOverride": 6248, "noPropertyAccessFromIndexSignature": 6248,
    "allowUnusedLabels": 6248, "allowUnreachableCode": 6248,
    "skipDefaultLibCheck": 6257, "skipLibCheck": 6257,
    "disableSizeLimit": 6249, "plugins": 6249,
}
# Options with no category in the compiler table. "ta" = Type Acquisition.
EXTRA_CATEGORY = {
    "files": 0, "include": 0, "exclude": 0, "references": 0, "extends": 0,
    "clean": 6171, "force": 6171, "verbose": 6171, "locale": 6171,
    "watchFile": 6250, "watchDirectory": 6250, "fallbackPolling": 6250,
    "synchronousWatchDirectory": 6250, "stopBuildOnErrors": 6250,
    "typeAcquisition": "ta", "enable": "ta", "excludeFiles": "ta",
    "excludeDirectories": "ta", "disableFilenameBasedTypeAcquisition": "ta",
}

# Sidebar navigation, mirroring handbookPages in
# packages/documentation/scripts/generateDocsNavigationPerLanguage.js.
# Item forms: "source/rel path.md", ("section", "Title", [items]),
# ("href", "Title", "/site/url"). "What's New" and "TSConfig Reference"
# are generated automatically.
NAV = [
    ("Get Started", [
        "get-started/TS for the New Programmer.md",
        "get-started/TS for JS Programmers.md",
        "get-started/TS for OOPers.md",
        "get-started/TS for Functional Programmers.md",
        "tutorials/TypeScript Tooling in 5 minutes.md",
    ]),
    ("Handbook", [
        "handbook-v2/The Handbook.md",
        "handbook-v2/Basics.md",
        "handbook-v2/Everyday Types.md",
        "handbook-v2/Narrowing.md",
        "handbook-v2/More on Functions.md",
        "handbook-v2/Object Types.md",
        ("section", "Type Manipulation", [
            "handbook-v2/Type Manipulation/_Creating Types from Types.md",
            "handbook-v2/Type Manipulation/Generics.md",
            "handbook-v2/Type Manipulation/Keyof Type Operator.md",
            "handbook-v2/Type Manipulation/Typeof Type Operator.md",
            "handbook-v2/Type Manipulation/Indexed Access Types.md",
            "handbook-v2/Type Manipulation/Conditional Types.md",
            "handbook-v2/Type Manipulation/Mapped Types.md",
            "handbook-v2/Type Manipulation/Template Literal Types.md",
        ]),
        "handbook-v2/Classes.md",
        "handbook-v2/Modules.md",
    ]),
    ("Reference", [
        "reference/Utility Types.md",
        ("href", "Cheat Sheets", "/cheatsheets"),
        "reference/Decorators.md",
        "reference/Declaration Merging.md",
        "reference/Enums.md",
        "reference/Iterators and Generators.md",
        "reference/JSX.md",
        "reference/Mixins.md",
        "reference/Namespaces.md",
        "reference/Namespaces and Modules.md",
        "reference/Symbols.md",
        "reference/Triple-Slash Directives.md",
        "reference/Type Compatibility.md",
        "reference/Type Inference.md",
        "reference/Variable Declarations.md",
    ]),
    ("Modules Reference", [
        "modules-reference/Introduction.md",
        "modules-reference/Theory.md",
        ("section", "Guides", [
            "modules-reference/guides/Choosing Compiler Options.md",
        ]),
        "modules-reference/Reference.md",
        ("section", "Appendices", [
            "modules-reference/appendices/ESM-CJS-Interop.md",
        ]),
    ]),
    ("Tutorials", [
        "tutorials/ASP.NET Core.md",
        "tutorials/Gulp.md",
        "tutorials/DOM Manipulation.md",
        "tutorials/Migrating from JavaScript.md",
        "tutorials/Babel with TypeScript.md",
    ]),
    ("What's New", "release-notes"),
    ("Declaration Files", [
        "declaration-files/Introduction.md",
        "declaration-files/By Example.md",
        "declaration-files/Library Structures.md",
        ("section", ".d.ts Templates", [
            "declaration-files/templates/module.d.ts.md",
            "declaration-files/templates/module-plugin.d.ts.md",
            "declaration-files/templates/module-class.d.ts.md",
            "declaration-files/templates/module-function.d.ts.md",
            "declaration-files/templates/global.d.ts.md",
            "declaration-files/templates/global-modifying-module.d.ts.md",
        ]),
        "declaration-files/Do's and Don'ts.md",
        "declaration-files/Deep Dive.md",
        "declaration-files/Publishing.md",
        "declaration-files/Consumption.md",
    ]),
    ("JavaScript", [
        "javascript/Intro to JS with TS.md",
        "javascript/Type Checking JavaScript Files.md",
        "javascript/JSDoc Reference.md",
        "javascript/Creating DTS files From JS.md",
    ]),
    ("Project Configuration", [
        "project-config/tsconfig.json.md",
        "project-config/Compiler Options in MSBuild.md",
        ("href", "TSConfig Reference", "/tsconfig"),
        "project-config/Compiler Options.md",
        "project-config/Project References.md",
        "project-config/Integrating with Build Tools.md",
        "project-config/Configuring Watch.md",
        "Nightly Builds.md",
    ]),
    ("TSConfig Reference", "tsconfig"),
]

# ----------------------------------------------------------- file mapping --

def slugify_name(name):
    """'Everyday Types.md' -> 'everyday-types.md' (dots are kept)."""
    stem = name[:-3] if name.endswith(".md") else name
    return slugify_stem(stem) + ".md"


def slugify_stem(stem):
    stem = stem.replace("'", "").replace("’", "").replace("_", " ")
    stem = stem.strip().lower()
    stem = re.sub(r"\s+", "-", stem)
    stem = re.sub(r"[^a-z0-9.\-]", "", stem)
    return stem.strip("-.")


def doc_out_rel(src_rel):
    """Map a path relative to copy/en to the vault-relative output path."""
    if src_rel == "Nightly Builds.md":
        return "project-config/nightly-builds.md"
    parts = src_rel.split("/")
    if parts[0] == "handbook-v2":
        parts[0] = "handbook"
    dirs = [slugify_stem(p) for p in parts[:-1]]
    return "/".join(dirs + [slugify_name(parts[-1])])


def collect_doc_files():
    """src rel (copy/en) -> out rel, skipping handbook-v1 and diagram sources."""
    files = {}
    for root, dirs, names in os.walk(DOCS):
        for name in names:
            if not name.endswith(".md"):
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, DOCS).replace("\\", "/")
            if rel.startswith("handbook-v1/") or rel.startswith("modules-reference/diagrams/"):
                continue
            files[rel] = doc_out_rel(rel)
    return files


def collect_tsconfig_files():
    """src rel (tsconfig copy/en) -> out rel for the tsconfig section."""
    files = {"intro.md": "tsconfig/intro.md", "cli/help.md": "tsconfig/cli-help.md"}
    secs = os.path.join(TSCONFIG, "sections")
    for name in os.listdir(secs):
        if name.endswith(".md"):
            files["sections/" + name] = "tsconfig/" + slugify_name(name)
    opts = os.path.join(TSCONFIG, "options")
    for name in os.listdir(opts):
        if name.endswith(".md"):
            # option names are camelCase flag names; keep them verbatim so
            # /tsconfig#flag anchors map 1:1 onto file names
            files["options/" + name] = "tsconfig/" + name
    return files


# ------------------------------------------------------------- frontmatter --

def parse_frontmatter(text):
    """Very small YAML-frontmatter reader: flat 'key: value' pairs only."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = {}
    for line in text[3:end].split("\n"):
        m = re.match(r"^(\w+):\s*(.*?)\s*$", line)
        if m and m.group(2):
            fm[m.group(1)] = m.group(2).strip('"').strip("'")
    return fm, text[end + 4:].lstrip("\n")


# --------------------------------------------------------------- converter --

INLINE_CODE_SPLIT_RE = re.compile(r"(`+[^`]*`+)")
LINK_RE = re.compile(r"\]\(((?:https?://(?:www\.)?typescriptlang\.org)?/[^)\s]*)\)")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
DIRECTIVE_RE = re.compile(r"^\s*//\s*@(?!(?:ts|TS)-)[A-Za-z][\w.-]*\s*(:.*)?$")
FILENAME_RE = re.compile(r"^\s*//\s*@[Ff]ilename:\s*(.+?)\s*$")
CARET_RE = re.compile(r"^\s*//\s*\^\?\s*$")
BARE_ANCHOR_RE = re.compile(r"\]\(#([^)\s]+)\)")
# fenced code blocks, possibly inside a blockquote (> ) or a list (indent)
FENCE_LINE_RE = re.compile(r"^((?:>\s*)*\s{0,3})(```+|~~~+)(.*)$")

# permalink aliases for site URLs that have no matching file permalink
EXTRA_ALIASES = {
    "/docs/handbook/modules.html": "modules-reference/introduction.md",
    "/docs/handbook/modules.html#export--and-import--require":
        "modules-reference/reference.md#export--and-import--require",
}


class Converter:
    def __init__(self, resolver, out_rel, tsconfig_anchors=None):
        self.resolver = resolver        # permalink/url -> vault rel path
        self.out_rel = out_rel          # vault-relative path of current file
        # bare #anchor -> page remap for tsconfig pages (the site renders all
        # options on a single page, so #optionName links are cross-page here)
        self.tsconfig_anchors = tsconfig_anchors
        self.images = {}                # absolute source path -> vault-relative path
        self.lines = []
        self.fence = None               # (marker, lang, prefix, is_twoslash) or None
        self.buf = []                   # buffered content lines of the active fence

    def emit(self, text=""):
        self.lines.append(text)

    def emit_prefixed(self, prefix, text=""):
        if prefix and text:
            self.emit(prefix + text)
        elif prefix:
            self.emit(prefix.rstrip())
        else:
            self.emit(text)

    def rel_link(self, target_rel):
        src_dir = os.path.dirname(self.out_rel)
        return os.path.relpath(target_rel, src_dir).replace("\\", "/")

    def resolve_url(self, url):
        # absolute typescriptlang.org URLs are treated like root-relative ones
        url = re.sub(r"^https?://(www\.)?typescriptlang\.org", "", url)
        path, _, anchor = url.partition("#")
        clean = path.rstrip("/")
        candidates = []
        if anchor:
            # /tsconfig#flag keys are stored with their anchor
            candidates.append(clean + "#" + anchor)
        candidates.append(clean)
        if clean.endswith(".html"):
            candidates.append(clean[:-5])
        for candidate in candidates:
            if candidate and candidate in self.resolver:
                target = self.resolver[candidate]
                if "#" in target:
                    # resolver entry carries its own anchor (e.g. a heading
                    # inside a tsconfig option page); it wins over the link's
                    target, anchor = target.split("#", 1)
                elif "#" in candidate:
                    # anchor was fully resolved into the target page itself
                    # (e.g. /tsconfig#strict -> tsconfig/strict.md)
                    anchor = ""
                suffix = ("#" + anchor) if anchor else ""
                return self.rel_link(target) + suffix
        return SITE + path + ("#" + anchor if anchor else "")

    def register_image(self, src):
        """Copy-target mapping for /images/... references; return relative link."""
        abs_src = os.path.join(STATIC, src.lstrip("/").replace("/", os.sep))
        vault_rel = src.lstrip("/")  # images/...
        self.images[abs_src] = vault_rel
        src_dir = os.path.dirname(self.out_rel)
        return os.path.relpath(vault_rel, src_dir).replace("\\", "/")

    def rewrite_inline(self, text):
        parts = INLINE_CODE_SPLIT_RE.split(text)
        return "".join(
            part if part.startswith("`") else self._rewrite_text(part)
            for part in parts
        )

    def _rewrite_text(self, text):
        # images first: LINK_RE would otherwise swallow the ](/images/...) part
        def img_sub(m):
            alt, src = m.group(1), m.group(2)
            if src.startswith("http"):
                return m.group(0)
            if src.startswith("/"):
                return "![%s](%s)" % (alt, self.register_image(src))
            return m.group(0)  # relative refs (modules-reference SVGs) stay as-is
        text = IMG_RE.sub(img_sub, text)
        text = LINK_RE.sub(lambda m: "](" + self.resolve_url(m.group(1)) + ")", text)
        if self.tsconfig_anchors:
            text = BARE_ANCHOR_RE.sub(self._bare_anchor_sub, text)
        return text

    def _bare_anchor_sub(self, m):
        anchor = m.group(1)
        target = self.tsconfig_anchors.get(anchor)
        if target is None:
            target = self.tsconfig_anchors.get(anchor.lower())
        if target is None:
            decoded = anchor.replace("%20", " ")
            target = (self.tsconfig_anchors.get(decoded)
                      or self.tsconfig_anchors.get(decoded.lower()))
        if target is None:
            return m.group(0)
        if "#" in target:
            page, anchor = target.split("#", 1)
            return "](%s#%s)" % (self.rel_link(page), anchor)
        return "](%s)" % self.rel_link(target)

    # -- main loop ----------------------------------------------------------

    def convert(self, body):
        # multiline HTML comments may contain fenced blocks; Obsidian renders
        # comments as nothing anyway, so drop them up front
        body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
        for raw in body.split("\n"):
            line = raw.rstrip()
            self.process_line(line)
        self.flush_fence()
        out = "\n".join(self.lines)
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out.strip() + "\n"

    def process_line(self, line):
        if self.fence:
            marker, _lang, prefix, _ts = self.fence
            content = line[len(prefix):] if prefix and line.startswith(prefix) else line
            m = FENCE_LINE_RE.match(content)
            if m and m.group(2).startswith(marker[0]) and not m.group(3).strip():
                self.flush_fence()
            else:
                self.buf.append(content)
            return

        m = FENCE_LINE_RE.match(line)
        if m:
            prefix, marker, info = m.group(1), m.group(2), m.group(3).strip()
            tokens = info.split()
            lang = tokens[0].lower() if tokens else ""
            is_twoslash = "twoslash" in tokens or "twslash" in tokens
            self.fence = (marker, lang, prefix, is_twoslash)
            self.buf = []
            return

        self.emit(self.rewrite_inline(line))

    def flush_fence(self):
        """Emit the buffered fence. Blocks with // @filename: markers are split
        into per-file fenced blocks preceded by a bold file name; twoslash
        blocks additionally get directives and ^? markers stripped."""
        if self.fence is None:
            return
        marker, lang, prefix, is_twoslash = self.fence
        lines, self.buf, self.fence = self.buf, [], None

        if is_twoslash or any(FILENAME_RE.match(l) for l in lines):
            parts = []          # list of [filename or None, [lines]]
            current = [None, []]
            for line in lines:
                fm = FILENAME_RE.match(line)
                if fm:
                    parts.append(current)
                    current = [fm.group(1), []]
                else:
                    current[1].append(line)
            parts.append(current)
            for fname, part_lines in parts:
                if is_twoslash:
                    part_lines = [l for l in part_lines
                                  if not DIRECTIVE_RE.match(l) and not CARET_RE.match(l)]
                while part_lines and not part_lines[0].strip():
                    part_lines.pop(0)
                while part_lines and not part_lines[-1].strip():
                    part_lines.pop()
                if not part_lines and fname is None:
                    continue
                self.emit_prefixed(prefix)
                if fname:
                    self.emit_prefixed(prefix, "**%s**" % fname)
                    self.emit_prefixed(prefix)
                self.emit_prefixed(prefix, marker + lang)
                for l in part_lines:
                    self.emit_prefixed(prefix, l)
                self.emit_prefixed(prefix, marker)
            self.emit_prefixed(prefix)
            return
        self.emit_prefixed(prefix, marker + lang)
        for l in lines:
            self.emit_prefixed(prefix, l)
        self.emit_prefixed(prefix, marker)


# --------------------------------------------------------- anchor fixing --

ANCHOR_LINK_RE = re.compile(r"\[((?:\[[^\]]*\]|[^\]\[])*)\]\(([^)#\s]+\.md)?#([^)\s]+)\)")


def fix_anchor_links(path, heading_maps):
    """Rewrite #anchor links (GitHub slugs) to Obsidian format (#Heading text).
    Anchors with no matching heading (stale upstream links) are degraded:
    cross-file links keep the page, same-file links keep just the text."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    rel = os.path.relpath(path, DST).replace("\\", "/")
    src_dir = os.path.dirname(rel)

    def sub(m):
        label, target, anchor = m.group(1), m.group(2), m.group(3)
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
            if target:
                print("STRIP ANCHOR: %s -> %s#%s" % (rel, target, anchor), file=sys.stderr)
                return "[%s](%s)" % (label, target)
            print("STRIP LINK: %s -> #%s" % (rel, anchor), file=sys.stderr)
            return label
        heading = heading.replace("(", "%28").replace(")", "%29")
        return "[%s](%s#%s)" % (label, target or "", heading)

    fixed = ANCHOR_LINK_RE.sub(sub, text)
    if fixed != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(fixed)
        return True
    return False


def fix_all_anchors():
    heading_maps = {}
    for root, _dirs, names in os.walk(DST):
        for name in names:
            if name.endswith(".md"):
                path = os.path.join(root, name)
                rel = os.path.relpath(path, DST).replace("\\", "/")
                with open(path, encoding="utf-8") as f:
                    heading_maps[rel] = extract_headings(f.read())
    fixed = 0
    for root, _dirs, names in os.walk(DST):
        for name in names:
            if name.endswith(".md"):
                if fix_anchor_links(os.path.join(root, name), heading_maps):
                    fixed += 1
    print("Fixed anchor links in %d files." % fixed)


# ------------------------------------------------------------------- index --

def build_resolver(doc_files, ts_files):
    """permalink -> vault-relative output path (may carry a #anchor)."""
    resolver = {}
    for src_rel, out_rel in list(doc_files.items()) + list(ts_files.items()):
        base = DOCS if src_rel in doc_files else TSCONFIG
        with open(os.path.join(base, src_rel), encoding="utf-8") as f:
            fm, _ = parse_frontmatter(f.read())
        permalink = fm.get("permalink")
        if permalink:
            resolver[permalink] = out_rel
            if permalink.endswith(".html"):
                resolver[permalink[:-5]] = out_rel
    # deprecated handbook-v1 permalinks redirect to their v2 replacements
    v1 = os.path.join(DOCS, "handbook-v1")
    for name in os.listdir(v1):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(v1, name), encoding="utf-8") as f:
            fm, _ = parse_frontmatter(f.read())
        permalink, target = fm.get("permalink"), fm.get("deprecated_by")
        if permalink and target:
            t_path, _, t_anchor = target.partition("#")
            out = resolver.get(t_path) or resolver.get(t_path.rstrip("/"))
            if out:
                resolver[permalink] = out + ("#" + t_anchor if t_anchor else "")
    # tsconfig single-page anchors: option name or heading inside an option page
    option_heads = {}  # github slug -> option out_rel
    for src_rel, out_rel in ts_files.items():
        if not src_rel.startswith("options/"):
            continue
        name = os.path.basename(src_rel)[:-3]
        resolver.setdefault("/tsconfig#" + name, out_rel)
        with open(os.path.join(TSCONFIG, src_rel), encoding="utf-8") as f:
            for slug in extract_headings(f.read()):
                option_heads.setdefault(slug, out_rel)
    for slug, out_rel in option_heads.items():
        resolver.setdefault("/tsconfig#" + slug, out_rel + "#" + slug)
    resolver["/tsconfig"] = "tsconfig/intro.md"
    resolver["/tsconfig.html"] = "tsconfig/intro.md"
    resolver.update(EXTRA_ALIASES)
    return resolver


def generate_index(titles, doc_files, ts_files, resolver):
    lines = ["# TypeScript Documentation Index", ""]
    lines.append("Source: [typescriptlang.org](%s) (offline snapshot)." % SITE)
    lines.append("")

    referenced = set()

    def emit_items(items, depth):
        for item in items:
            pad = "  " * depth
            if isinstance(item, str):
                out_rel = doc_files.get(item)
                if not out_rel:
                    print("INDEX: missing file %s" % item, file=sys.stderr)
                    continue
                referenced.add(out_rel)
                lines.append("%s- [%s](%s)" % (pad, titles[out_rel], out_rel))
            elif item[0] == "section":
                lines.append("%s- **%s**" % (pad, item[1]))
                emit_items(item[2], depth + 1)
            elif item[0] == "href":
                internal = resolver.get(item[2])
                if internal:
                    referenced.add(internal)
                    lines.append("%s- [%s](%s)" % (pad, item[1], internal))
                else:
                    lines.append("%s- [%s](%s%s)" % (pad, item[1], SITE, item[2]))

    for title, items in NAV:
        lines.append("## %s" % title)
        lines.append("")
        if items == "release-notes":
            notes = sorted((s for s in doc_files if s.startswith("release-notes/")),
                           reverse=True)
            for src_rel in notes:
                out_rel = doc_files[src_rel]
                referenced.add(out_rel)
                lines.append("- [%s](%s)" % (titles[out_rel], out_rel))
        elif items == "tsconfig":
            emit_tsconfig_index(lines, titles, ts_files)
        else:
            emit_items(items, 0)
        lines.append("")

    # pages that exist but are not part of the site's sidebar navigation
    leftovers = {}
    for src_rel, out_rel in sorted(doc_files.items(), key=lambda kv: kv[1]):
        if out_rel in referenced:
            continue
        top = out_rel.split("/")[0]
        leftovers.setdefault(top, []).append(out_rel)
    if leftovers:
        lines.append("## Other Pages")
        lines.append("")
        for top, rels in sorted(leftovers.items()):
            lines.append("**%s**" % top)
            lines.append("")
            for out_rel in rels:
                lines.append("- [%s](%s)" % (titles[out_rel], out_rel))
            lines.append("")

    with open(os.path.join(DST, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def emit_tsconfig_index(lines, titles, ts_files):
    lines.append("- [%s](%s)" % (titles["tsconfig/intro.md"], "tsconfig/intro.md"))
    for src_rel, out_rel in sorted(ts_files.items()):
        if src_rel.startswith("sections/") or src_rel == "cli/help.md":
            lines.append("- [%s](%s)" % (titles[out_rel], out_rel))
    lines.append("")
    categories = {}  # code -> (display title, [option names])
    cat_titles = category_titles()
    for src_rel, out_rel in sorted(ts_files.items()):
        if not src_rel.startswith("options/"):
            continue
        name = os.path.basename(src_rel)[:-3]
        code = OPTION_CATEGORY.get(name, EXTRA_CATEGORY.get(name))
        if code is None:
            code = "misc"
        categories.setdefault(code, []).append(name)
    def sort_key(code):
        return (1, 0) if code == "misc" else (0, code if isinstance(code, int) else 9999)
    for code in sorted(categories, key=sort_key):
        if code == "misc":
            title = "Miscellaneous"
        elif code == "ta":
            title = "Type Acquisition"
        else:
            title = cat_titles.get(code, "Category %s" % code)
        lines.append("**%s**" % title)
        lines.append("")
        for name in sorted(categories[code], key=str.lower):
            lines.append("- [`%s`](tsconfig/%s.md)" % (name, name))
        lines.append("")


def build_tsconfig_anchors(ts_files):
    """bare #anchor -> tsconfig page remap: option names, section names and
    heading slugs inside option pages (the site renders all of these on one
    page, so same-page anchors are cross-page links in the vault)."""
    anchors = {}
    for src_rel, out_rel in ts_files.items():
        if src_rel.startswith("options/"):
            name = os.path.basename(src_rel)[:-3]
            anchors[name] = out_rel
            with open(os.path.join(TSCONFIG, src_rel), encoding="utf-8") as f:
                for slug in extract_headings(f.read()):
                    anchors.setdefault(slug, out_rel + "#" + slug)
        elif src_rel.startswith("sections/"):
            stem = os.path.basename(src_rel)[:-3]
            anchors[stem] = out_rel
            anchors[stem.lower()] = out_rel
    return anchors


def category_titles():
    """category code -> display title, from categories/<Name>_<code>.md files."""
    titles = {}
    cats = os.path.join(TSCONFIG, "categories")
    for name in os.listdir(cats):
        m = re.match(r".+_(\d+)\.md$", name)
        if not m:
            continue
        with open(os.path.join(cats, name), encoding="utf-8") as f:
            fm, _ = parse_frontmatter(f.read())
        titles[int(m.group(1))] = fm.get("display", name[:-3].replace("_", " "))
    return titles


# ------------------------------------------------------------------- main --

def main():
    doc_files = collect_doc_files()
    ts_files = collect_tsconfig_files()
    resolver = build_resolver(doc_files, ts_files)
    tsconfig_anchors = build_tsconfig_anchors(ts_files)
    os.makedirs(DST, exist_ok=True)

    titles = {}
    all_images = {}
    for base, files in ((DOCS, doc_files), (TSCONFIG, ts_files)):
        for src_rel, out_rel in sorted(files.items()):
            with open(os.path.join(base, src_rel), encoding="utf-8") as f:
                text = f.read()
            fm, body = parse_frontmatter(text)
            title = fm.get("title")
            if not title and fm.get("display") and src_rel.startswith("options/"):
                title = "`%s`" % os.path.basename(src_rel)[:-3]
            if not title:
                title = fm.get("display") or fm.get("header")
            if not title:
                heading = re.search(r"^#{1,3}\s+(.+)$", body, re.M)
                if heading:
                    # promote the first heading to the page title
                    title = heading.group(1).strip()
                    body = (body[:heading.start()] + body[heading.end():]).lstrip("\n")
            if not title:
                title = os.path.basename(src_rel)[:-3].replace("-", " ").title()
            anchors = tsconfig_anchors if base == TSCONFIG else None
            conv = Converter(resolver, out_rel, anchors)
            converted = "# %s\n\n%s" % (title, conv.convert(body))
            out_path = os.path.join(DST, out_rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(converted)
            titles[out_rel] = title
            all_images.update(conv.images)

    # copy /images/* referenced by the docs
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

    # copy modules-reference SVG diagrams (referenced by relative links)
    diagrams = os.path.join(DOCS, "modules-reference", "diagrams")
    svg_count = 0
    for name in os.listdir(diagrams):
        if name.endswith(".svg"):
            dst = os.path.join(DST, "modules-reference", "diagrams", name)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(diagrams, name), dst)
            svg_count += 1

    generate_index(titles, doc_files, ts_files, resolver)
    fix_all_anchors()
    print("Converted %d files, copied %d images + %d diagrams (%d missing)."
          % (len(titles), copied, svg_count, missing))


if __name__ == "__main__":
    main()
