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
   - Set `isWeak=True` ONLY if an entity cannot be uniquely identified by its own attributes alone and depends on an owner entity for identification and existence (e.g., 'Room' dependent on 'Resort', 'Cargo_Hold' dependent on 'Vessel').
   - For all regular entities with their own unique identifier, set `isWeak=False`.

2. ATTRIBUTES:
   - Primary Keys: Set `isPrimaryKey=True` ONLY for attributes that uniquely identify a strong entity. Weak entities must NOT have `isPrimaryKey=True`.
   - Partial Keys (Discriminators): For weak entities, set `isPartialKey=True` on the attribute that distinguishes weak entity instances within the same owner entity (e.g., 'room_number' for Room, 'hold_number' for Cargo_Hold, 'dependent_name' for Dependent). Strong entities must NOT have `isPartialKey=True`.
   - Derived Attributes: Set `isDerived=True` for attributes whose values are dynamically calculated or derived from other attributes or relationships rather than stored directly (e.g., 'age' derived from 'birth_date', 'total_value', 'years_of_service', 'total_capacity').
   - Multivalued Attributes: Set `isMultiValued=True` for attributes that can hold multiple distinct values per entity instance (e.g., contact numbers, locations, frequencies).
   - Composite Attributes: Set `composite` to a list of sub-attribute names if an attribute is divisible into smaller component attributes (e.g., 'name' -> ['first_name', 'last_name']).
   - Simple Attributes: Leave all boolean flags as `False` and `composite=null`.

3. RELATIONSHIPS (BINARY & N-ARY):
   - Model all interactions between entities as relationships.
   - Set `isIdentifying=True` ONLY for the relationship connecting a weak entity to its owner/identifying entity. For all standard relationships between strong entities, set `isIdentifying=False`.
   - Participants: Every relationship MUST contain a `participants` array detailing each connected entity:
     * Binary relationships have 2 participant objects.
     * Ternary and N-ary relationships have 3 or more participant objects connected to a single relationship diamond.
   - For each item in `participants`:
     * `entity`: Must match the exact name of an entity defined in the `entities` array.
     * `cardinality`: Use standard Chen single-character tokens: '1', 'N', 'M', or 'P'.
     * `participation`: Specify strictly as "total" (mandatory) or "partial" (optional). Default to "partial" if not explicitly required.
     - Relationship Attributes: If an interaction or event records its own descriptive attributes (e.g., 'StartDate' on WorksIn, 'Grade' on EnrolledIn, 'SupplyDate' and 'Quantity' on Supplies, or 'BorrowDate'/'DueDate' on Borrows), place them inside the relationship's `attributes` list rather than on an entity.
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