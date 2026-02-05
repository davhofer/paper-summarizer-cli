import pymupdf
import re
import tempfile
import os
import argparse
import subprocess
import requests
from pathlib import Path


PROMPT = """You are a Research Assistant, an expert in academic analysis and scientific communication. Your role is to help researchers quickly grasp the core value and methodology of complex papers.

When analyzing a paper, your summary must follow this exact structure:

1.  **Core Contributions**: What is the primary novelty or value-add of this work?
2. **Background**: A very short summary of the most relevant background required to understand what the authors did and the main contributions.
2.  **What the Authors Did**: A detailed look at the methodology, experiments, or theoretical framework employed.
3.  **Key Findings**: The most significant results and data points.
4.  **Noteworthy Discussion**: Interesting insights, limitations, and future directions mentioned by the authors.

Guidelines:
- Maintain academic rigor while being clear and concise.
- Use precise terminology from the relevant field.
- Your output should be clean Markdown, ready to be saved as a .md file.
- Use markdown titles/headers for the paper title and the 4 sections ('#' and '##')

Analyze the research paper at the following filepath and provide a structured summary according to the structure above. Output only the formatted summary and nothing else.
"""

DEFAULT_OUTPUT_DIR = "~/Documents/papers/summaries/"
DEFAULT_MODEL = "gemini-2.5-flash"


def find_reference_page(pdf_path):
    """
    Identifies the page number (0-indexed) where the references section starts.
    Returns None if not found.
    """
    doc = pymupdf.open(pdf_path)

    # Regex to capture standalone headers.
    header_pattern = re.compile(
        r"^\s*(?:\d+\.?\s*)?(references|bibliography|works cited|literature cited)\s*$",
        re.IGNORECASE,
    )

    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")

        for block in blocks:
            block_text = block[4]
            lines = block_text.split("\n")

            for line in lines:
                clean_line = line.strip()

                if header_pattern.match(clean_line):
                    # HEURISTIC CHECK: False Positive Prevention
                    if page_num < len(doc) * 0.1:
                        continue

                    return page_num  # Return 0-indexed page number

    return None


def extract_pages_until(pdf_path, last_page_index):
    """
    Creates a temporary PDF containing pages from the start up to last_page_index (inclusive).
    Returns the path to the temporary PDF.
    """
    doc = pymupdf.open(pdf_path)
    new_doc = pymupdf.open()

    # insert_pdf uses 0-indexed page numbers.
    # to_page is inclusive.
    new_doc.insert_pdf(doc, from_page=0, to_page=last_page_index)

    # Create a temporary file path
    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    new_doc.save(temp_path)
    new_doc.close()
    doc.close()

    return temp_path


def download_arxiv_pdf(url):
    """
    Downloads a PDF from an arXiv URL (abstract or PDF link).
    Returns the path to the temporary PDF.
    """
    # Convert abstract URL to PDF URL
    # https://arxiv.org/abs/2507.19457 -> https://arxiv.org/pdf/2507.19457
    pdf_url = url.replace("/abs/", "/pdf/")
    if not pdf_url.endswith(".pdf") and "/pdf/" in pdf_url:
        # arXiv PDF links usually don't end in .pdf, but let's ensure it looks right
        pass

    print(f"Downloading from: {pdf_url}")
    response = requests.get(pdf_url, stream=True)
    response.raise_for_status()

    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return temp_path


def main():
    parser = argparse.ArgumentParser(
        description="Summarize a PDF paper excluding references."
    )
    parser.add_argument(
        "input_path", help="Path to the PDF file or arXiv URL to summarize."
    )
    parser.add_argument(
        "--dir",
        help=f"Output directory.  (default: {DEFAULT_OUTPUT_DIR})",
        default=DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument(
        "--model",
        help=f"Specify the version of gemini to be used.  (default: {DEFAULT_MODEL})",
        default=DEFAULT_MODEL,
    )
    args = parser.parse_args()

    input_path = args.input_path
    temp_download = None

    if input_path.startswith(("http://", "https://")):
        if "arxiv.org" in input_path:
            try:
                temp_download = download_arxiv_pdf(input_path)
                pdf_path = Path(temp_download)
            except Exception as e:
                print(f"Error downloading arXiv PDF: {e}")
                return
        else:
            print("Error: Only arXiv URLs are supported at this time.")
            return
    else:
        pdf_path = Path(input_path)
        if not pdf_path.exists():
            print(f"Error: File {pdf_path} does not exist.")
            return

    print(f"Processing: {pdf_path.name}")
    page_index = find_reference_page(str(pdf_path))

    if page_index is not None and page_index > 0:
        print(
            f"Found references at page {page_index}. Extracting pages 0 to {page_index - 1}..."
        )
        temp_pdf = extract_pages_until(str(pdf_path), page_index - 1)
        target_pdf = temp_pdf
    else:
        print("References not found or start at page 0. Using original PDF.")
        target_pdf = str(pdf_path)
        temp_pdf = None

    try:
        print("Running gemini...")
        target_pdf_path = Path(target_pdf).resolve()
        full_prompt = f"{PROMPT}\nFilepath: {target_pdf_path.name}"

        cmd = ["gemini", "--model", args.model, "-p", full_prompt]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=str(target_pdf_path.parent),
        )
        summary_content = result.stdout

        output_dir = Path(args.dir).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)

        summary_filename = f"summary_{pdf_path.stem}.md"
        # If it was a temp file from arXiv, the stem might be random, so let's try to get a better name if possible
        if temp_download and "arxiv.org" in input_path:
            arxiv_id = input_path.split("/")[-1]
            summary_filename = f"summary_arxiv_{arxiv_id}.md"

        output_path = output_dir / summary_filename

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary_content)

        print(f"Summary saved to: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error running gemini command: {e}")
        print(f"Stderr: {e.stderr}")
    finally:
        if temp_pdf and os.path.exists(temp_pdf):
            os.remove(temp_pdf)
        if temp_download and os.path.exists(temp_download):
            os.remove(temp_download)


if __name__ == "__main__":
    main()
