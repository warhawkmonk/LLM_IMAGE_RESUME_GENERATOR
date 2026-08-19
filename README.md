# Resume Image to PDF Generator

This project turns a resume design image into a printable HTML resume and a PDF.
It uses a vision-capable LLM to reproduce the layout as HTML, then uses
[WeasyPrint](https://weasyprint.org/) to render the HTML at a fixed page size.

## How It Works

1. Read a reference resume image from `image_folder`.
2. Encode the image as Base64.
3. Send the image and a resume-generation prompt to the configured LLM API.
4. Save the generated HTML to `output/index/index.html`.
5. Render that HTML to `output/pdf/output.pdf` with a 1000 x 1400 pixel page and zero margins.

The complete workflow is stored in [`resume.ipynb`](resume.ipynb).

## Requirements

- Python 3.10 or newer
- A working internet connection for the LLM API request
- An accessible LLM endpoint that accepts the request format used by the notebook
- Python packages listed in [`requirements.txt`](requirements.txt)

Install the dependencies in a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The notebook also imports `requests` and `weasyprint`. If they are not already
listed in the requirements file, install them explicitly:

```powershell
python -m pip install requests weasyprint
```

## Usage

1. Open `resume.ipynb` in VS Code or Jupyter.
2. Select the virtual environment containing the installed dependencies.
3. Put the reference image at `image_folder\res-2.jpg`, or update the image path in the second cell.
4. Run the cells from top to bottom.
5. Inspect the generated files:

   - HTML: `output/index/index.html`
   - PDF: `output/pdf/output.pdf`

The generated HTML is also useful for checking or manually refining the layout
before creating the PDF again.

## Configuration

The main settings are in the notebook:

| Setting | Purpose |
| --- | --- |
| `url` | LLM API endpoint used to generate the HTML |
| `image_path` | Reference resume image path |
| `PAGE_WIDTH_PX` | PDF page width, default `1000` |
| `PAGE_HEIGHT_PX` | PDF page height, default `1400` |
| `SCALE` | CSS scale applied during PDF rendering, default `1.0` |
| `INPUT_FILE` | Generated HTML input path |
| `OUTPUT_FILE` | Generated PDF output path |

The API currently receives the image as `image_b64` and the prompt with
`image_understanding` set to `True`. Configure authentication in the request
headers if the API requires it. Do not commit API keys or other credentials to
the notebook.

## Project Structure

```text
pdf generator/
├── image_folder/
│   └── res-2.jpg              # Reference resume design
├── output/
│   ├── index/
│   │   └── index.html         # LLM-generated resume HTML
│   └── pdf/
│       └── output.pdf         # Rendered resume PDF
├── requirements.txt
├── resume.ipynb               # End-to-end workflow
└── README.md
```

## Troubleshooting

### The API request fails

Check the endpoint URL, network connection, request payload, and any required
authentication headers. The notebook currently returns `response.text`, so the
API response should be inspected before writing it to the HTML file.

### The output contains Markdown fences

The notebook removes an opening ```` ```html ```` fence and the final closing
fence when the model returns fenced HTML. The prompt also asks the model to
return HTML only.

### Images or styles are missing in the PDF

Use paths that are available to WeasyPrint and keep important styles inline or
in accessible local files. Check `output/index/index.html` in a browser first
to separate HTML/CSS issues from PDF-rendering issues.

### The PDF is clipped or has unexpected whitespace

Adjust `PAGE_WIDTH_PX`, `PAGE_HEIGHT_PX`, or `SCALE` in the final notebook cell.
The current CSS intentionally removes outer margins and padding from common
resume wrapper elements.

## Security and Privacy

Resume images may contain personal information. Review the privacy policy of
the configured LLM service before sending images to it, and avoid storing API
credentials or sensitive generated data in source control.
