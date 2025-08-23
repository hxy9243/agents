# Librarian Agent

This project implements a "Librarian Agent" that allows users to interact with a library management system through a conversational interface. The agent is built using the Model Context Protocol (MCP), FastMCP, and DSPy.

# Quick Start

* Python 3.9 or higher
* `uv` for dependency management

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/hxy9243/agents.git
    cd agents/librarian
    ```

2.  Install the dependencies:
    ```bash
    uv sync
    ```

## Running the Project

1.  **Start the MCP Server**:
    ```bash
    uv run python mcp_service.py
    ```
    This will start the MCP server on `http://localhost:5400`.

2.  **Run the Librarian Agent**:

    In a separate terminal, run the following command:
    ```bash
    # set the correct example Auth token, e.g. token_001 for user alice
    export TEST_TOKEN=token_001
    uv run python assistant.py
    ```

    Enters the eval loop:

    ```
    Welcome, user Alice
    Library > Do you have the book 1984?
    ```

    This will start the librarian agent and you can start interacting with it.

## Interacting with the Agent

Once the agent is running, you can interact with it by typing your requests in the terminal. Here are some examples:

*   **Search for books**:
    ```
    Library > Do you have the book 1984?
    ```

*   **Borrow a book**:
    ```
    Library > I want to borrow a copy of hitchhiker's guide
    ```

*   **Check your loans**:
    ```
    Library > What books have I borrowed?
    ```


# Project Overview

The project consists of three main components:

1.  **Library Implementation**: A naive "Library" library (sorry) that provides basic CRUD functionalities. The data is stored in-memory.
2.  **MCP Server**: A server built with FastMCP that exposes the library's functionalities as a set of tools and resources over HTTP. It also demos the auth for MCP server.
3.  **Librarian Assistant with DSPy**: A conversational agent built with DSPy that connects to the MCP server, lists the available tools, and uses a ReAct module to interact with the user and the library tools.

