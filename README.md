# AI-Powered ER Diagram Generator

## Overview
An end-to-end pipeline that parses structured JSON schemas or natural language database descriptions into Chen-notation Entity-Relationship (ER) diagrams using Google's Gemini API and Graphviz.

## Features
- **Part 1 (Renderer):** Parses ER definitions into graphical representations adhering to Chen notation:
  - Entities as rectangular boxes.
  - Primary key attributes as underlined ellipses.
  - Multivalued attributes as double ellipses.
  - Composite attributes hierarchically branching from parent attribute nodes.
  - Relationships as diamond nodes with labeled edge cardinalities (`1:1`, `1:N`, `M:N`).
- **Part 2 (AI Extraction):** Uses Gemini (`gemini-3.8-flash`) with structured schema enforcement via Pydantic to convert unstructured text descriptions directly into the required JSON schema without parsing errors.

## Installation & Setup
1. **System Dependencies:**
   - Requires Graphviz installed and added to the system PATH:
     ```powershell
     winget install Graphviz.Graphviz
     ```
2. **Python Environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. **Environment Configuration:**
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

### 1. Direct JSON Mode (Part 1)
To generate an ER diagram directly from a structured JSON file:
```powershell
python main.py --json-file data/sample_data.json --output output/er_part1
```

### 2. Natural Language AI Mode (Part 2)
To generate both the structured JSON and the visual ER diagram from a plain text requirement file:
```powershell
python main.py --text-file data/prompt_example.txt --output output/er_part2
```