# Paper Summarizer

A CLI tool to summarize PDF papers excluding references.

## Prerequisite

Ensure you have the [Gemini CLI](https://github.com/google/gemini-cli) installed and configured on your system.

## Installation

Install the tool directly from GitHub using `uv`:

```bash
uv tool install git+https://github.com/davhofer/paper-summarizer-cli.git
```

## Usage

```bash
# Using a local file
summarize path/to/your/paper.pdf

# Using an arXiv URL (abstract or PDF)
summarize https://arxiv.org/abs/2507.19457

# Specifying a custom output directory
summarize path/to/your/paper.pdf --dir ./my_summaries

# Using a specific Gemini model
summarize path/to/your/paper.pdf --model gemini-2.0-flash
```

This will:
1. Identify the reference section.
2. Extract all pages before the references.
3. Use the `gemini` CLI to summarize the content.
4. Save the summary as a Markdown file to `~/Documents/papers/summaries/` (or your specified `--dir`).

## Model Customization

By default, the tool uses `gemini-2.5-flash`. You can specify a different model using the `--model` flag. Available models typically include:


* `gemini-2.5-flash`: (Default) Optimized for speed and low latency.
* `gemini-3-pro-preview`: The most capable model, ideal for complex reasoning (requires "Preview Features" to be enabled).
* `gemini-3-flash-preview`: Faster and more efficient for routine tasks (requires "Preview Features" to be enabled).
* `gemini-2.5-pro`: A balanced, high-performance model.
* `gemini-2.5-flash-lite`: The lightest and fastest model for simple tasks.
* `auto`: Allows the system to automatically select the most appropriate model based on the complexity of your request.
