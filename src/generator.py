import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.models import ERDiagram

# Load environment variables from .env
load_dotenv()

SYSTEM_INSTRUCTION = """
You are an expert database designer and data modeler.
Your task is to analyze natural language database descriptions and extract the Entity-Relationship (ER) model.

Follow these strict rules:
1. Identify all primary entities.
2. For each entity, extract:
   - Primary key attributes (mark isPrimaryKey=True).
   - Multivalued attributes like phone numbers or locations (mark isMultiValued=True).
   - Composite attributes broken down into their constituent components in the composite array.
   - Simple attributes.
3. Identify all relationships between pairs of entities:
   - Use descriptive relationship names (e.g., 'Works_In', 'Manages', 'Enrolls').
   - Specify the cardinality strictly using the format: '1:1', '1:N', 'M:N', or 'N:1'.
"""


def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is missing. "
            "Set it in your .env file or system environment."
        )
    return genai.Client(api_key=api_key)


def generate_er_diagram_from_text(
    description: str, model_name: str = "gemini-3.8-flash"
) -> ERDiagram:
    client = get_gemini_client()
    response = client.models.generate_content(
        model=model_name,
        contents=description,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=ERDiagram,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini API returned an empty response.")
    return ERDiagram.model_validate_json(response.text)