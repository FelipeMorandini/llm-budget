# Installation

## Basic Install

=== "pip"

    ```bash
    pip install llm-toll
    ```

=== "uv"

    ```bash
    uv add llm-toll
    ```

=== "poetry"

    ```bash
    poetry add llm-toll
    ```

The base package has **zero dependencies** -- it works with the Python standard library alone.

## Optional Extras

Install provider-specific extras to enable SDK auto-detection:

```bash
# OpenAI SDK support
pip install llm-toll[openai]

# Anthropic SDK support
pip install llm-toll[anthropic]

# Google Gemini SDK support
pip install llm-toll[gemini]

# PostgreSQL backend for team-wide tracking
pip install llm-toll[postgres]

# Everything
pip install llm-toll[all]
```

## Requirements

- Python 3.10 or later
- No required runtime dependencies

!!! note
    The optional extras install the respective SDK packages (`openai`, `anthropic`, `google-genai`, `psycopg2-binary`) which are needed only if you want automatic response parsing for that provider. You can always use the `extract_usage` callback for manual extraction without installing any extras.

## Verify Installation

```python
import llm_toll
print(llm_toll.__version__)
```

```bash
llm-toll --version
```
