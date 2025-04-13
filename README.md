# Agents

A collection of experimental AI agent implementations - personal explorations in AI agent development.

# Quick Start

This project uses Poetry for dependency and environment management. First install Poetry:

```bash
pip3 install poetry

# Activate virtual environment and install dependencies
poetry shell
poetry install
```

And fill in the environment with your model name and your personal key in local `.env`. See `.env.example`..

```
LM_BASE_URL=
LM_API_KEY=
LM_MODEL_NAME=
EMBED_MODEL_NAME=
```

# run the actual scripts, for example

```
poetry run therapist
```

# Agent List

- **[Therapist](/therapist/)**

  The first toy example of AI agent implemented with DSPy. A very basic AI implemented therapist that can:

  - Have a conversation with you.
  - Summarize and memorize what you said across sessions (saved locally in DB).

  Example:

  ```
    poetry run therapist
    Starting conversation: hello world
    [2025-04-13 16:39:16] assistant: Hello world! I'm here to help you with any questions or problems. What's on your mind right now?
    [2025-04-13 16:39:22] user: I'm feeling down.
    [2025-04-13 16:39:25] assistant: I hear that you're feeling down, and I want you to know that it's okay to feel this way. Can you tell me more about what's been going on or what might be contributing to these feelings? I'm here to listen and help you work through this.
    user:
  ```

# Contribution

You can help by:

- File a bug for any problems you see.
- Create a new issue for any idea of improvements or new projects you might have.
- Send a Pull Request for small fixes.
