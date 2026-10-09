import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.models import ERDiagram

# Load environment variables from .env
load_dotenv()

SYSTEM_INSTRUCTION = """
You are an expert database designer and data modeler.
Your task is to analyze natural language database descriptions and extract the Entity-Relationship (ER) model adhering strictly to the Chen ER modeling methodology.

Follow these strict rules:

1. Entities and Weak Entities:
   - Identify all entities.
   - Set `isWeak=True` ONLY for weak entities. A weak entity is an entity that cannot be uniquely identified by its own attributes alone and existence-depends on an owner/identifying entity (e.g., 'Dependent' depending on 'Employee').
   - For all regular (strong) entities, set `isWeak=False`.

2. Attributes:
   - Primary Keys: Set `isPrimaryKey=True` for attributes that uniquely identify a strong entity.
   - Multivalued Attributes: Set `isMultiValued=True` for attributes that can hold multiple values for a single entity instance (e.g., phone numbers, skill sets, office locations).
   - Composite Attributes: Provide a list of sub-component names in the `composite` array (e.g., 'Name' with composite ['FirstName', 'LastName']).
   - Simple Attributes: Leave flags as default False and composite as null.

3. Relationships and Identifying Relationships:
   - Connect pairs of entities using descriptive relationship names (e.g., 'Works_In', 'Manages', 'Has_Dependent').
   - Identifying Relationships: Set `isIdentifying=True` ONLY for the relationship connecting a weak entity to its owner entity. For all standard relationships between strong entities, set `isIdentifying=False`.
   - Cardinality: Specify strictly in the format '1:1', '1:N', 'M:N', or 'N:1' (representing the ratio between entity1 and entity2).

4. Participation Constraints:
   - For each relationship, specify `entity1Participation` and `entity2Participation` strictly as either "total" or "partial":
     * "total": Every single instance of the entity must participate in the relationship (mandatory participation; e.g., a weak entity always has total participation in its identifying relationship; or "each employee MUST belong to a department").
     * "partial": Participation is optional for entity instances (e.g., "an employee may manage a department").
     * Default to "partial" if not explicitly stated or implied as mandatory.
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