# 📄 PDF Generator

A simple Python-based tool to convert **Markdown**, **HTML** (raw strings, local files, or URLs) into professional **PDF documents**.

---

## ✨ Features

- ✅ Convert **Markdown files (.md)** to PDF
- ✅ Convert **HTML strings** directly to PDF
- ✅ Generate PDF from **local HTML files**
- ✅ Create PDF from **URLs/websites**
- ✅ Customizable page size (A4, Letter, Legal, etc.)
- ✅ Set margins for proper document spacing
- ✅ Add page numbers to your PDF
- ✅ Support for landscape orientation
- ✅ Extra wkhtmltopdf options for advanced customization

---

## 📦 Requirements

```bash
pip install markdown>=3.5 pdfkit>=1.0 Pygments>=2.16
```

**Note:** You also need **wkhtmltopdf** installed on your system:

### Windows
- Download from: https://wkhtmltopdf.org/downloads.html
- Install and ensure `wkhtmltopdf.exe` is in your `PATH`, OR specify the path when converting.
- Default locations checked:
  - `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`
  - `C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe`

---

## 🚀 Quick Start

### Example 1: Convert a Markdown file to PDF

```python
from html_to_pdf import html_to_pdf

# Create PDF from your markdown file
html_text = """
# Sample Document

This is a sample document.
"""

result = html_to_pdf(html_text, "output.pdf")
print(f"PDF created: {result}")
```

### Example 2: Convert an HTML string to PDF

```python
html_string = """
<html>
<head>
    <style>
        body { font-family: Arial; }
        h1 { color: navy; }
    </style>
</head>
<body>
    <h1>Welcome!</h1>
    <p>This is a styled PDF document.</p>
</body>
</html>
"""

html_to_pdf(html_string, "styled.pdf")
```

### Example 3: Convert from an HTML file

```python
html_to_pdf("index.html", "from_file.pdf")
```

### Example 4: Convert a URL to PDF

```python
html_to_pdf("https://example.com", "website.pdf")
```

---

## 🔧 Function API

```python
def html_to_pdf(
    source: str,          # HTML string, file path, or URL
    output_path: str = "output.pdf",   # Output PDF filename
    page_size: str = "A4",            # Page size: A4, Letter, Legal, etc.
    margins: str = "18mm",            # CSS-style margin (e.g., "1in", "0.5cm")
    page_numbers: bool = False,       # Add page numbers to footer
    landscape: bool = False,          # Use landscape orientation
    wkhtmltopdf_path: str = None,    # Optional path to wkhtmltopdf.exe
    extra_options: dict = None        # Additional wkhtmltopdf options
) -> Path:
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `source` | `str` | HTML string, local file path, or URL |
| `output_path` | `str` | Output PDF filename/directory |
| `page_size` | `str` | Page size (`A4`, `Letter`, `Legal`, etc.) |
| `margins` | `str` | Margin value (e.g., `"18mm"`, `"1in"`) |
| `page_numbers` | `bool` | Add "Page X of Y" footer |
| `landscape` | `bool` | Use landscape orientation |
| `wkhtmltopdf_path` | `str` | Optional explicit path to wkhtmltopdf.exe |
| `extra_options` | `dict` | Additional wkhtmltopdf configuration options |

### Example with custom options

```python
html_to_pdf(
    "<h1>Title</h1><p>Content</p>",
    "styled_output.pdf",
    page_size="A4",
    margins="0.5in",
    page_numbers=True,
    landscape=False,
    extra_options={
        "footer-right": "[date]",        # Show date on footer right
        "disable-smart-shrinking": None  # Disable shrinking
    }
)
```

---

## 🖥️ Command Line Usage

Run from the command line:

```bash
python html_to_pdf.py file.md -o output.pdf
python html_to_pdf.py https://example.com -o website.pdf --page-size A4
python html_to_pdf.py document.html -o myfile.pdf --landscape --page-numbers
```

Options:

```
html_to_pdf.py: convert HTML (string, file, or URL) to PDF

positional arguments:
  source         HTML file path or URL

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output PDF path (default: output.pdf)
  --page-size PAGE_SIZE
                        Page size (e.g. A4, Letter)
  --landscape           Use landscape orientation
  --page-numbers        Enable page numbers in footer
```

---

## 📝 Supported Formats

| Input Type | Description |
|------------|-------------|
|.md files | Markdown documents |
|.html/.htm files | Local HTML files |
| Raw HTML strings | Direct HTML content |
|URLs|Websites and web pages |

---

## 🔍 Troubleshooting

### "wkhtmltopdf not found" Error

Make sure wkhtmltopdf is installed:

1. Visit https://wkhtmltopdf.org/downloads.html
2. Download and install the official patched version
3. Add to PATH or specify path explicitly via `wkhtmltopdf_path` parameter

### Single-Page/Poor Quality PDFs

This may be caused by using an unpatched (distro-packaged) wkhtmltopdf build:

```bash
# Check current wkhtmltopdf version
wkhtmltopdf --version

# You should see "(with patched qt)" in the output
```

If not shown, install the [official patched build](https://wkhtmltopdf.org/downloads.html).

### Common Issues

- **Images not showing**: Use absolute paths or `enable-local-file-access` option
- **Links don't work**: URLs are converted directly; relative links may break when converting local files

---

## 📂 Project Structure

```
pdf generator/
├── html_to_pdf.py     # Main conversion module
├── requirements.txt   # Python dependencies
├── input.md           # Sample Markdown (resume)
├── index.html         # Sample HTML file
├── output.pdf         # Generated PDF output
└── env/               # Python virtual environment
```

---

## 📄 License

MIT License - Feel free to use this tool for personal or commercial projects.

---

## 🤝 Contributing

Feel free to fork and submit issues or pull requests!
