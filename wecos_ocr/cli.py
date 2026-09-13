"""Command-Line Interface for wecos-ocr."""

import argparse
import sys
from pathlib import Path

from .pipeline import convert_pdf_to_md, transcribe


def main():
    parser = argparse.ArgumentParser(
        prog="wecos-ocr",
        description="Sovereign Myanmar Optical Character Recognition & Syllable CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: image
    img_parser = subparsers.add_parser("image", help="Transcribe a single image file")
    img_parser.add_argument("path", type=Path, help="Path to input image (JPG, PNG, WebP)")
    img_parser.add_argument("--backend", default="ollama", choices=["ollama", "tesseract"], help="Inference backend")
    img_parser.add_argument("--model", default="wecos-myanmar-ocr-qwen3:8b", help="Ollama model name")
    img_parser.add_argument("--no-enhance", action="store_true", help="Disable adaptive vision enhancement")
    img_parser.add_argument("--no-repair", action="store_true", help="Disable orthographic spell correction")

    # Command: pdf
    pdf_parser = subparsers.add_parser("pdf", help="Convert a PDF document to Markdown")
    pdf_parser.add_argument("path", type=Path, help="Path to input PDF file")
    pdf_parser.add_argument("-o", "--output", type=Path, default=None, help="Output markdown file path")
    pdf_parser.add_argument("--backend", default="ollama", choices=["ollama", "tesseract"], help="Inference backend")
    pdf_parser.add_argument("--model", default="wecos-myanmar-ocr-qwen3:8b", help="Ollama model name")
    pdf_parser.add_argument("--dpi", type=int, default=150, help="Rendering DPI")
    pdf_parser.add_argument("--no-enhance", action="store_true", help="Disable adaptive vision enhancement")
    pdf_parser.add_argument("--no-repair", action="store_true", help="Disable orthographic spell correction")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "image":
        if not args.path.exists():
            print(f"Error: File not found: {args.path}", file=sys.stderr)
            sys.exit(1)
        res = transcribe(
            args.path,
            backend=args.backend,
            model=args.model,
            enhance=not args.no_enhance,
            repair=not args.no_repair,
        )
        print(res.text)

    elif args.command == "pdf":
        if not args.path.exists():
            print(f"Error: File not found: {args.path}", file=sys.stderr)
            sys.exit(1)
        md = convert_pdf_to_md(
            args.path,
            output_md=args.output,
            backend=args.backend,
            model=args.model,
            dpi=args.dpi,
            enhance=not args.no_enhance,
            repair=not args.no_repair,
        )
        if not args.output:
            print(md)
        else:
            print(f"Successfully converted {args.path} to {args.output}")


if __name__ == "__main__":
    main()
