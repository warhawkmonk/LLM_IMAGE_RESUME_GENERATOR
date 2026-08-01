"""
html_to_pdf — Convert any HTML (raw string, local file, or URL) to PDF.

Uses wkhtmltopdf under the hood via pdfkit. Works with plain HTML,
inline <style> blocks, and CSS driven by @media print rules.

Requirements:
    pip install pdfkit --break-system-packages
    wkhtmltopdf must be installed on the system (https://wkhtmltopdf.org/downloads.html)

Usage:
    from html_to_pdf import html_to_pdf

    html_to_pdf("<h1>Hello</h1><p>World</p>", "out.pdf")
    html_to_pdf("report.html", "out.pdf")                 # local file
    html_to_pdf("https://example.com", "out.pdf")          # URL
"""

from pathlib import Path
import shutil
import sys


def _find_wkhtmltopdf(explicit_path: str = None) -> str:
    """Locate the wkhtmltopdf executable, or raise a clear error."""
    if explicit_path:
        if not Path(explicit_path).exists():
            raise FileNotFoundError(f"wkhtmltopdf not found at {explicit_path}")
        return explicit_path

    found = shutil.which("wkhtmltopdf") or shutil.which("wkhtmltopdf.exe")
    if found:
        return found

    for path in (
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        "/usr/local/bin/wkhtmltopdf",
    ):
        if Path(path).exists():
            return path

    raise FileNotFoundError(
        "wkhtmltopdf not found. Install it from "
        "https://wkhtmltopdf.org/downloads.html and either add it to PATH "
        "or pass wkhtmltopdf_path explicitly."
    )


def _warn_if_unpatched(wkhtmltopdf_exe: str) -> None:
    """Best-effort warning for distro-packaged (unpatched Qt) builds.

    Those builds commonly truncate output to a single page, drop
    headers/footers, or ignore print CSS. See wkhtmltopdf.org for the
    official patched build if you hit that.
    """
    import subprocess

    try:
        result = subprocess.run(
            [wkhtmltopdf_exe, "--version"], capture_output=True, text=True, timeout=10
        )
        version_output = (result.stdout + result.stderr).lower()
    except Exception:
        return

    if "patched qt" not in version_output:
        print(
            "Warning: this wkhtmltopdf build doesn't report '(with patched qt)'. "
            "Distro packages (apt/yum/brew) commonly cause single-page or "
            "truncated PDFs — if you hit that, install the official build "
            "from https://wkhtmltopdf.org/downloads.html.",
            file=sys.stderr,
        )


def _looks_like_url(source: str) -> bool:
    return source.startswith("http://") or source.startswith("https://")


def _looks_like_file(source: str) -> bool:
    # Treat as a file path only if it exists on disk — avoids misreading
    # a raw HTML string that happens to be short.
    try:
        return Path(source).is_file()
    except OSError:
        return False


def html_to_pdf(
    source: str,
    output_path: str = "output.pdf",
    page_size: str = "A4",
    margins: str = "18mm",
    page_numbers: bool = False,
    landscape: bool = False,
    wkhtmltopdf_path: str = None,
    extra_options: dict = None,
) -> Path:
    """
    Convert HTML to a PDF file.

    Args:
        source: Raw HTML string, a path to a local .html file, or a URL.
        output_path: Where to write the PDF.
        page_size: e.g. "A4", "Letter", "Legal".
        margins: CSS-style margin applied to all four sides, e.g. "18mm", "1in".
        page_numbers: If True, adds a "Page X of Y" footer.
        landscape: If True, renders in landscape orientation.
        wkhtmltopdf_path: Optional explicit path to the wkhtmltopdf binary.
        extra_options: Additional raw wkhtmltopdf options to merge in/override,
            e.g. {"footer-right": "[date]", "disable-smart-shrinking": None}.

    Returns:
        Path to the generated PDF.
    """
    import pdfkit

    wkhtmltopdf_exe = _find_wkhtmltopdf(wkhtmltopdf_path)
    _warn_if_unpatched(wkhtmltopdf_exe)
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_exe)

    output_path = str(Path(output_path).with_suffix(".pdf"))

    options = {
        "page-size": page_size,
        "margin-top": margins,
        "margin-bottom": margins,
        "margin-left": margins,
        "margin-right": margins,
        "encoding": "UTF-8",
        "enable-local-file-access": None,  # lets local <img>/<link> paths resolve
        "print-media-type": None,
        "quiet": None,
    }
    if landscape:
        options["orientation"] = "Landscape"
    if page_numbers:
        options["footer-center"] = "Page [page] of [topage]"
        options["footer-font-size"] = "8"
        options["footer-spacing"] = "5"
    if extra_options:
        options.update(extra_options)

    if _looks_like_url(source):
        pdfkit.from_url(source, output_path, options=options, configuration=config)
    elif _looks_like_file(source):
        pdfkit.from_file(source, output_path, options=options, configuration=config)
    else:
        pdfkit.from_string(source, output_path, options=options, configuration=config)

    return Path(output_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert HTML (string, file, or URL) to PDF.")
    parser.add_argument("source", help="HTML file path or URL")
    parser.add_argument("-o", "--output", default="output.pdf", help="Output PDF path")
    parser.add_argument("--page-size", default="A4")
    parser.add_argument("--landscape", action="store_true")
    parser.add_argument("--page-numbers", action="store_true")
    args = parser.parse_args()

    result = html_to_pdf(
        args.source,
        output_path=args.output,
        page_size=args.page_size,
        landscape=args.landscape,
        page_numbers=args.page_numbers,
    )
    print(f"PDF written to: {result}")