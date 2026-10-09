import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.models import ERDiagram

# Load environment variables from .env
load_dotenv()

SYSTEM_INSTRUCTION = """
You are a principal database architect and expert data modeler.
Your task is to analyze natural language database requirements and extract a rigorous Entity-Relationship (ER) model adhering strictly to classical Chen ER modeling conventions.

You must output a structured JSON model adhering to the following rules:

1. ENTITIES & WEAK ENTITIES:
   - Identify every distinct entity set.
   - Set `isWeak=True` ONLY if an entity cannot be uniquely identified by its own attributes alone and depends on an owner entity for identification and existence (e.g., 'Room' dependent on 'Resort', 'Dependent' dependent on 'Employee').
   - For all regular entities with their own unique identifier, set `isWeak=False`.

2. ATTRIBUTES:
   - Primary Keys: Set `isPrimaryKey=True` only for attributes that uniquely identify a strong entity. Weak entities must NOT have `isPrimaryKey=True` attributes.
   - Multivalued Attributes: Set `isMultiValued=True` for attributes that can hold multiple distinct values per entity instance (e.g., contact numbers, locations, skills).
   - Composite Attributes: Set `composite` to a list of sub-attribute names if an attribute is divisible into smaller component attributes (e.g., 'name' -> ['first_name', 'last_name']; 'address' -> ['street', 'city', 'zip']).
   - Simple Attributes: Leave `isPrimaryKey=False`, `isMultiValued=False`, and `composite=null`.

3. RELATIONSHIPS (BINARY & N-ARY):
   - Model all interactions between entities as relationships.
   - Set `isIdentifying=True` ONLY for the relationship connecting a weak entity to its owner/identifying entity. For all standard relationships between strong entities, set `isIdentifying=False`.
   - Participants: Every relationship MUST contain a `participants` array detailing each connected entity:
     * Binary relationships have exactly 2 participant objects.
     * Ternary and N-ary relationships connect 3 or more participant objects to a single relationship diamond (e.g., 'Supplies' connecting 'Supplier', 'Part', and 'Project').
   - For each item in `participants`:
     * `entity`: Must match the exact name of an entity defined in the `entities` array.
     * `cardinality`: The structural ratio for this leg. Use standard Chen single-character tokens: '1', 'N', 'M', or 'P'.
     * `participation`: Specify strictly as "total" or "partial".
       - "total": Every instance of the entity must mandatorily participate in this relationship (e.g., a weak entity always has total participation in its identifying relationship; or requirements state "every X must have a Y").
       - "partial": Optional participation (e.g., "an employee may manage a department"). Default to "partial" if mandatory participation is not explicitly required.
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
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=ERDiagram,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini API returned an empty response.")
    return ERDiagram.model_validate_json(response.text)