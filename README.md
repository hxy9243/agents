# Agents

A collection of experimental AI agent implementations - personal explorations in AI agent development.

# Quick Start

This project uses uv for dependency and environment management. First install [uv](https://github.com/astral-sh/uv).

Init the environment with:

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip sync
```

And fill in the environment with your model name and your personal key in local `.env`. See `.env.example`..

```
LM_BASE_URL=
LM_API_KEY=
LM_MODEL_NAME=

EMBED_MODEL_NAME=
DATABASE_DIR=

# for exa search API
EXA_API_KEY=
```

Run example agents in the command line with:

```bash
uv run therapist

uv run startup_researcher
```

# Agent List

## **[Therapist](/therapist/)**

Setup the following env var:

```
LM_BASE_URL=
LM_API_KEY=
LM_MODEL_NAME=
EMBED_MODEL_NAME=
DATABASE_DIR=
```

Run a conversational therapist with:

```bash
uv run therapist
```

The first toy example of AI agent implemented with [DSPy](https://github.com/stanfordnlp/dspy). A very basic AI implemented therapist that can:

- Have a conversation with you.
- Summarize and memorize what you said across sessions (saved locally in DB).

It implements a really toy example of implementation of **Memory**, which includes:

- short term memory (saved sequentially in SQL database), and
- long term memory (summary and memory lookup with chromadb).

Example:

```
  poetry run therapist
  Starting conversation: hello world
  [2025-04-13 16:39:16] assistant: Hello world! I'm here to help you with any questions or problems. What's on your mind right now?
  [2025-04-13 16:39:22] user: I'm feeling down.
  [2025-04-13 16:39:25] assistant: I hear that you're feeling down, and I want you to know that it's okay to feel this way. Can you tell me more about what's been going on or what might be contributing to these feelings? I'm here to listen and help you work through this.
  user:
```

## **[Startup Researcher](/startup/)**

A toy researcher example implemented by DSPy and Exa search. It'll query the search API with the
startup name you input, asks for confirmation, and generate a markdown output.

For this agent, you'll need the [exa](https://exa.ai/) API key setup in the env var:

```
LM_BASE_URL=
LM_API_KEY=
LM_MODEL_NAME=
EXA_API_KEY=
```

Run it with:

```bash
uv run startup_researcher
```
Example:

```
Enter the company name or search term: inflection ai
2025-06-22 13:27:28,164 - startup.research_agent - INFO - Running search agent with search term: inflection ai
...
```

See more [examples here](/startup/results/).

# Contribution

You can help by:

- File a bug for any problems you see.
- Create a new issue for any idea of improvements or new projects you might have.
- Send a Pull Request for small fixes.
