# Chess Agents UI - MCP

A Python-based Chess GUI application that interfaces with Large Language Models (LLMs) via a Model Context Protocol (MCP) server to play chess.

## Overview

This project implements a chess application where users can play against AI agents powered by LLMs (specifically Google's Gemini, with placeholders for OpenAI). The architecture separates the user interface (Client) from the AI logic (MCP Server).

## Project Structure

```
/
├── agents/             # LLM Agent implementations
│   ├── llm_agents.py   # BaseAgent, GeminiAgent, OpenAIAgent classes
│   └── ...
├── client/             # Pygame-based Frontend
│   ├── main.py         # Entry point for the GUI
│   ├── styles.py       # UI constants and styling
│   ├── assets/         # Images and resources
│   └── ...
├── mcp_server/         # FastAPI Backend
│   ├── main.py         # Entry point for the server
│   ├── models/         # Pydantic models for API
│   └── ...
├── requirements.txt    # Project dependencies
└── ...
```

## Features

*   **Interactive GUI:** Built with `pygame`, featuring move highlighting, drag-and-drop (or click-click) interface, and a game clock.
*   **Game Modes:**
    *   **Player vs. Agent:** Play against the AI.
    *   **Agent vs. Agent:** Watch two AI agents play against each other.
*   **LLM Integration:** Uses `google-generativeai` to power the `GeminiAgent`. The agent provides:
    *   The best move.
    *   A short "trash talk" or commentary.
    *   A detailed explanation of the strategic reasoning.
*   **MCP Architecture:** The `mcp_server` exposes an API (`/move`) that the client consumes, decoupling the game state from the heavy lifting of the LLM.

## Design Patterns

*   **Client-Server Architecture:** The GUI runs locally and communicates with the `mcp_server` via HTTP JSON requests.
*   **Strategy Pattern:** `agents/llm_agents.py` defines a `BaseAgent` abstract class. Concrete implementations (`GeminiAgent`, `OpenAIAgent`) can be swapped easily.
*   **Factory Pattern:** The server initializes the appropriate agent based on the `LLM_AGENT_TYPE` configuration.

## Prerequisites

*   Python 3.9+
*   A Google Gemini API Key (or OpenAI Key if implementing that agent).

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd chess-agents-ui-mcp
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Set the following environment variables. You can export them in your shell or use a `.env` file manager if you prefer.
    
    *   `GEMINI_API_KEY`: Your Google Gemini API key.
    *   `LLM_AGENT_TYPE`: Set to `gemini`.

## Running the Application

This application requires two separate processes running simultaneously.

### 1. Start the MCP Server

The server handles the AI logic.

```bash
uvicorn mcp_server.main:app --reload
```
*The server will typically start on `http://127.0.0.1:8000`.*

### 2. Start the Client

Open a new terminal window and run the GUI.

```bash
python client/main.py
```

## Libraries Used

*   **FastAPI & Uvicorn:** For the high-performance web server.
*   **Pygame:** For the graphical user interface.
*   **Python-Chess:** For robust chess rules validation and board state management.
*   **Google-GenerativeAI:** For interacting with the Gemini model.
*   **Requests:** For HTTP communication between client and server.
