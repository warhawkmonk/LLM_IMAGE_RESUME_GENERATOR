#!/usr/bin/env python3
"""
test2.py — A module with functions accessible from both cmd and Python scripts.

Usage from cmd:
    python test2.py convert input.md output.pdf --theme light
    python test2.py info input.md

Usage from Python:
    from test2 import convert, info, list_files
    convert("input.md", "output.pdf", theme="dark")
"""

import argparse
import os
from pathlib import Path
import sys


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
DEFAULT_OUTPUT_SUFFIX = ".pdf"
DEFAULT_THEME = "light"
SUPPORTED_THEMES = ["light", "dark"]


def convert(input_path: str, output_path: str = None, theme: str = DEFAULT_THEME) -> str:
    """
    Convert a Markdown file to PDF with the specified theme.
    
    Args:
        input_path: Path to the input .md file
        output_path: Path to the output .pdf file (default: same name as input)
        theme: Visual theme ('light' or 'dark')
    
    Returns:
        Path to the generated PDF file
    
    Raises:
        FileNotFoundError: If the input file doesn't exist
        ValueError: If an unsupported theme is provided
    """
    input_file = Path(input_path)
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if theme not in SUPPORTED_THEMES:
        raise ValueError(f"Unsupported theme '{theme}'. Supported themes: {SUPPORTED_THEMES}")
    
    # Generate output path if not provided
    if output_path is None:
        output_path = str(input_file.with_suffix(DEFAULT_OUTPUT_SUFFIX))
    else:
        output_path = str(Path(output_path).with_suffix(DEFAULT_OUTPUT_SUFFIX))
    
    # Import and use the conversion function from test.py
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from test import convert as _convert
    
    _convert(
        input_file,
        Path(output_path),
        theme=theme,
        include_toc=True,
        page_numbers=True,
        page_size="A4",
        wkhtmltopdf_path=None,
    )
    
    return output_path


def info(input_path: str) -> dict:
    """
    Get information about a Markdown file.
    
    Args:
        input_path: Path to the input .md file
    
    Returns:
        Dictionary containing file information:
            - name: Filename
            - path: Absolute path
            - size_bytes: File size in bytes
            - line_count: Number of lines
            - word_count: Approximate word count
            - has_code_blocks: Whether the file contains code blocks
            - has_tables: Whether the file contains tables
    
    Raises:
        FileNotFoundError: If the input file doesn't exist
    """
    input_file = Path(input_path)
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    content = input_file.read_text(encoding="utf-8")
    lines = content.split('\n')
    
    # Count code blocks (``` markers)
    has_code_blocks = '```' in content
    
    # Detect tables (simple detection based on | characters in multiple lines)
    table_lines = [line for line in lines if '|' in line]
    has_tables = len(table_lines) > 1
    
    return {
        "name": input_file.name,
        "path": str(input_file.absolute()),
        "size_bytes": input_file.stat().st_size,
        "line_count": len(lines),
        "word_count": len(content.split()) if content else 0,
        "has_code_blocks": has_code_blocks,
        "has_tables": has_tables,
    }


def list_files(directory: str = ".") -> list:
    """
    List Markdown files in a directory.
    
    Args:
        directory: Directory path (default: current directory)
    
    Returns:
        List of dictionaries containing file information
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    md_files = list(dir_path.glob("*.md"))
    
    return [info(str(file)) for file in md_files]


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Markdown to PDF conversion utility with file info inspection.",
        epilog="Examples:\n"
               "  python test2.py convert input.md output.pdf --theme dark\n"
               "  python test2.py info input.md\n"
               "  python test2.py list-files ../documents\n"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert Markdown to PDF")
    convert_parser.add_argument("input", type=str, help="Input .md file path")
    convert_parser.add_argument("-o", "--output", type=str, default=None, help="Output .pdf file path")
    convert_parser.add_argument("--theme", type=str, default=DEFAULT_THEME, choices=SUPPORTED_THEMES, help="Theme (light/dark)")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get file information")
    info_parser.add_argument("input", type=str, help="Input .md file path")
    
    # List-files command
    list_parser = subparsers.add_parser("list-files", help="List Markdown files in a directory")
    list_parser.add_argument("directory", type=str, nargs="?", default=".", help="Directory to search (default: current)")
    
    args = parser.parse_args()
    
    if args.command == "convert":
        try:
            output_path = convert(args.input, args.output, args.theme)
            print(f"✓ PDF generated: {output_path}")
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "info":
        try:
            file_info = info(args.input)
            print(f"File: {file_info['name']}")
            print(f"Path:  {file_info['path']}")
            print(f"Size:  {file_info['size_bytes']:,} bytes")
            print(f"Lines: {file_info['line_count']}")
            print(f"Words: {file_info['word_count']:,}")
            print(f"Code blocks: {'Yes' if file_info['has_code_blocks'] else 'No'}")
            print(f"Tables: {'Yes' if file_info['has_tables'] else 'No'}")
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "list-files":
        try:
            files = list_files(args.directory)
            if not files:
                print("No Markdown files found.")
            else:
                for file_info in files:
                    size_kb = file_info['size_bytes'] / 1024
                    print(f"{file_info['name']} ({size_kb:.1f} KB, {file_info['line_count']} lines)")
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
