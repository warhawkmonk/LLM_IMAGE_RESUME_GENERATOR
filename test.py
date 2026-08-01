#!/usr/bin/env python3
"""
md_to_pdf.py — Convert Markdown to a beautifully styled PDF.

Mimics the look of the popular VS Code "Markdown PDF" extension:
GitHub-flavoured typography, syntax-highlighted code blocks, clean
tables, blockquotes, and page numbers in the footer.

Pipeline:  Markdown --(python-markdown)--> HTML --(wkhtmltopdf)--> PDF

Usage:
    python3 md_to_pdf.py input.md
    python3 md_to_pdf.py input.md -o output.pdf
    python3 md_to_pdf.py input.md --theme dark
    python3 md_to_pdf.py input.md --no-toc --no-page-numbers
"""

import argparse
import shutil
import sys
from pathlib import Path

import markdown
import pdfkit
from pygments.formatters import HtmlFormatter

# --------------------------------------------------------------------------
# Locate the wkhtmltopdf executable.
#
# On Windows it usually is NOT on PATH after installation, so pdfkit can't
# find it automatically. We check PATH first, then fall back to the default
# install locations used by the official Windows installer.
# --------------------------------------------------------------------------
WINDOWS_DEFAULT_PATHS = [
    r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
    r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
]


def find_wkhtmltopdf(explicit_path: str = None) -> str:
    if explicit_path:
        if not Path(explicit_path).exists():
            print(f"Error: wkhtmltopdf not found at {explicit_path}", file=sys.stderr)
            sys.exit(1)
        return explicit_path

    on_path = shutil.which("wkhtmltopdf") or shutil.which("wkhtmltopdf.exe")
    if on_path:
        return on_path

    for candidate in WINDOWS_DEFAULT_PATHS:
        if Path(candidate).exists():
            return candidate

    print(
        "Error: could not find wkhtmltopdf.\n"
        "Install it from https://wkhtmltopdf.org/downloads.html and either:\n"
        "  - let the installer add it to PATH, or\n"
        "  - re-run with --wkhtmltopdf-path \"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe\"",
        file=sys.stderr,
    )
    sys.exit(1)

# --------------------------------------------------------------------------
# Themes — light mirrors GitHub's default markdown style (the extension's
# default); dark mirrors GitHub's dark mode.
# --------------------------------------------------------------------------
THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#24292f",
        "heading": "#1a1a1a",
        "muted": "#57606a",
        "border": "#d0d7de",
        "code_bg": "#f6f8fa",
        "link": "#0969da",
        "blockquote_border": "#d0d7de",
        "table_stripe": "#f6f8fa",
        "pygments_style": "default",
    },
    "dark": {
        "bg": "#0d1117",
        "fg": "#c9d1d9",
        "heading": "#e6edf3",
        "muted": "#8b949e",
        "border": "#30363d",
        "code_bg": "#161b22",
        "link": "#58a6ff",
        "blockquote_border": "#30363d",
        "table_stripe": "#161b22",
        "pygments_style": "monokai",
    },
}

CSS_TEMPLATE = """
@page {{
    margin: 20mm 18mm;
}}

* {{ box-sizing: border-box; }}

body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue",
                 Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    font-size: 11pt;
    line-height: 1.6;
    color: {fg};
    background: {bg};
    word-wrap: break-word;
}}

.markdown-body {{
    max-width: 100%;
    margin: 0 auto;
}}

/* Headings */
h1, h2, h3, h4, h5, h6 {{
    color: {heading};
    font-weight: 600;
    line-height: 1.25;
    margin-top: 24px;
    margin-bottom: 16px;
}}
h1 {{
    font-size: 2em;
    padding-bottom: 0.3em;
    border-bottom: 1px solid {border};
}}
h2 {{
    font-size: 1.5em;
    padding-bottom: 0.3em;
    border-bottom: 1px solid {border};
}}
h3 {{ font-size: 1.25em; }}
h4 {{ font-size: 1em; }}
h5 {{ font-size: 0.875em; }}
h6 {{ font-size: 0.85em; color: {muted}; }}

h1:first-child, h2:first-child {{ margin-top: 0; }}

p {{ margin-top: 0; margin-bottom: 16px; }}

a {{ color: {link}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* Lists */
ul, ol {{ margin-top: 0; margin-bottom: 16px; padding-left: 2em; }}
li {{ margin-top: 0.25em; }}
li > p {{ margin-top: 16px; }}

/* Blockquotes */
blockquote {{
    margin: 0 0 16px 0;
    padding: 0 1em;
    color: {muted};
    border-left: 0.25em solid {blockquote_border};
}}
blockquote > :first-child {{ margin-top: 0; }}
blockquote > :last-child {{ margin-bottom: 0; }}

/* Horizontal rule */
hr {{
    height: 0.25em;
    margin: 24px 0;
    background-color: {border};
    border: 0;
}}

/* Tables */
table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
    overflow: auto;
    display: block;
}}
table th, table td {{
    padding: 6px 13px;
    border: 1px solid {border};
}}
table th {{
    font-weight: 600;
    background-color: {code_bg};
}}
table tr:nth-child(2n) {{
    background-color: {table_stripe};
}}

/* Inline code */
code, tt {{
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 85%;
    background-color: {code_bg};
    padding: 0.2em 0.4em;
    border-radius: 6px;
}}

/* Code blocks */
pre {{
    background-color: {code_bg};
    border-radius: 6px;
    padding: 16px;
    overflow: auto;
    line-height: 1.45;
    margin-bottom: 16px;
    page-break-inside: avoid;
}}
pre code, pre tt {{
    background: transparent;
    padding: 0;
    font-size: 85%;
    white-space: pre-wrap;
    word-break: break-word;
}}

/* Images */
img {{ max-width: 100%; box-sizing: content-box; }}

/* Task lists */
.task-list-item {{ list-style-type: none; }}
.task-list-item input {{ margin: 0 0.5em 0.25em -1.6em; vertical-align: middle; }}

/* Footnotes */
.footnote {{ font-size: 0.85em; color: {muted}; }}

/* Table of contents */
.toc {{
    background-color: {code_bg};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 16px 24px;
    margin-bottom: 24px;
}}
.toc > ul {{ margin-bottom: 0; }}
.toclink {{ color: {link}; }}

/* Keep headings with following content where possible */
h1, h2, h3, h4, h5, h6 {{ page-break-after: avoid; }}
img, table {{ page-break-inside: avoid; }}

/* Pygments syntax highlighting */
{pygments_css}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<article class="markdown-body">
{content}
</article>
</body>
</html>
"""


def convert_markdown_to_html(md_text: str, include_toc: bool) -> str:
    """Convert markdown text to an HTML fragment."""
    extensions = [
        "extra",            # tables, fenced_code, footnotes, attr_list, etc.
        "codehilite",       # pygments syntax highlighting
        "sane_lists",
        "nl2br",
        "admonition",
        "meta",
    ]
    extension_configs = {
        "codehilite": {
            "guess_lang": False,
            "css_class": "codehilite",
        }
    }
    if include_toc:
        extensions.append("toc")
        extension_configs["toc"] = {"permalink": False, "title": "Table of Contents"}

    md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)
    html = md.convert(md_text)

    if include_toc and getattr(md, "toc", None):
        toc_html = md.toc
        # Only prepend a TOC block if there were actually headings to collect.
        if "<li>" in toc_html or "<a" in toc_html:
            html = f'<div class="toc">{toc_html}</div>\n{html}'

    return html


def build_html(md_text: str, title: str, theme: str, include_toc: bool) -> str:
    palette = THEMES[theme]
    pygments_css = HtmlFormatter(style=palette["pygments_style"]).get_style_defs(".codehilite")
    css = CSS_TEMPLATE.format(pygments_css=pygments_css, **palette)
    content = convert_markdown_to_html(md_text, include_toc)
    return HTML_TEMPLATE.format(title=title, css=css, content=content)


def convert(
    input_path: Path,
    output_path: Path,
    theme: str = "light",
    include_toc: bool = True,
    page_numbers: bool = True,
    page_size: str = "A4",
    wkhtmltopdf_path: str = None,
) -> None:
    md_text = input_path.read_text(encoding="utf-8")
    title = input_path.stem
    html = build_html(md_text, title=title, theme=theme, include_toc=include_toc)

    # Keep a copy of the intermediate HTML alongside the output — handy for
    # debugging styling and for previewing in a browser.
    debug_html_path = output_path.with_suffix(".html")
    debug_html_path.write_text(html, encoding="utf-8")

    wkhtmltopdf_exe = find_wkhtmltopdf(wkhtmltopdf_path)
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_exe)

    options = {
        "page-size": page_size,
        "margin-top": "20mm",
        "margin-bottom": "20mm",
        "margin-left": "18mm",
        "margin-right": "18mm",
        "encoding": "UTF-8",
        "enable-local-file-access": None,
        "print-media-type": None,
        "quiet": None,
    }
    if page_numbers:
        options["footer-center"] = "Page [page] of [topage]"
        options["footer-font-size"] = "8"
        options["footer-spacing"] = "5"
        options["footer-font-name"] = "Helvetica"

    pdfkit.from_string(html, str(output_path), options=options, configuration=config)


def main():
    parser = argparse.ArgumentParser(
        description="Convert a Markdown file into a beautifully styled PDF "
        "(GitHub-style typography, syntax-highlighted code, like the VS Code "
        "'Markdown PDF' extension)."
    )
    parser.add_argument("input", type=Path, help="Path to the input .md file")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Path to the output .pdf file (default: same name as input)"
    )
    parser.add_argument(
        "--theme", choices=THEMES.keys(), default="light",
        help="Visual theme (default: light)"
    )
    parser.add_argument(
        "--page-size", default="A4", help="Page size, e.g. A4, Letter (default: A4)"
    )
    parser.add_argument(
        "--no-toc", action="store_true", help="Do not generate a table of contents"
    )
    parser.add_argument(
        "--no-page-numbers", action="store_true", help="Do not print page numbers in the footer"
    )
    parser.add_argument(
        "--wkhtmltopdf-path", default=None,
        help=r'Full path to wkhtmltopdf.exe if it is not on PATH '
        r'(e.g. "C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")'
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or args.input.with_suffix(".pdf")

    convert(
        args.input,
        output_path,
        theme=args.theme,
        include_toc=not args.no_toc,
        page_numbers=not args.no_page_numbers,
        page_size=args.page_size,
        wkhtmltopdf_path=args.wkhtmltopdf_path,
    )
    print(f"✓ PDF written to {output_path}")


if __name__ == "__main__":
    main()