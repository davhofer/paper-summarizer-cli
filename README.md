# Paper Summarizer

A CLI tool to summarize PDF papers excluding references.

## Prerequisite

Ensure you have the [Gemini CLI](https://github.com/google/gemini-cli) installed and configured on your system. Additionally, in order to use Gemini 3 models, "Preview Features" need to be enabled in the settings.

## Installation

1.  **Install the tool** directly from GitHub using `uv`:

    ```bash
    uv tool install git+https://github.com/davhofer/paper-summarizer.git
    ```

2.  **Set up the Research Assistant Agent**: This tool uses a custom Gemini agent. You must copy the provided `research_assistant.toml` to your Gemini agents directory:

    ```bash
    mkdir -p ~/.gemini/agents
    cp research_assistant.toml ~/.gemini/agents/
    ```

### Model Customization

You can change the model used for summarization by editing the `model` field in `~/.gemini/agents/research_assistant.toml`. The following options are available:

*   `gemini-3-pro-preview`: The most capable model, ideal for complex reasoning (requires "Preview Features" to be enabled).
*   `gemini-3-flash-preview`: Faster and more efficient for routine tasks (requires "Preview Features" to be enabled).
*   `gemini-2.5-pro`: A balanced, high-performance model.
*   `gemini-2.5-flash`: Optimized for speed and low latency.
*   `gemini-2.5-flash-lite`: The lightest and fastest model for simple tasks.
*   `auto`: Allows the system to automatically select the most appropriate model based on the complexity of your request.

## Usage

```bash
# Using a local file
summarize path/to/your/paper.pdf

# Using an arXiv abstract URL
summarize https://arxiv.org/abs/2507.19457

# Using an arXiv PDF URL
summarize https://arxiv.org/pdf/2507.19457

# Specifying a custom output directory
summarize path/to/your/paper.pdf --dir ./my_summaries
```

This will:
1. Identify the reference section.
2. Extract all pages before the references.
3. Use `gemini research_assistant` to summarize the content.
4. Save the summary to `~/Documents/papers/summaries/` (or your specified `--dir`).
