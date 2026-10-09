import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.generator import generate_er_diagram_from_text
from src.renderer import render_er_diagram


def run_test():
    prompt = (
        "We are designing a hospital database. "
        "A Doctor has a national_id (primary key), a full_name consisting of first_name and last_name, "
        "and multiple contact_numbers. "
        "A Patient has a patient_id (primary key), an address consisting of street, city, and zip, "
        "and an age. "
        "A Doctor treats multiple Patients, and a Patient can be treated by multiple Doctors (cardinality M:N)."
    )

    print("Sending prompt to Gemini API...")
    diagram = generate_er_diagram_from_text(prompt)

    print("\n--- Extracted JSON Model ---")
    json_output = diagram.model_dump_json(indent=2, by_alias=True)
    print(json_output)

    # Save generated JSON
    os.makedirs("output", exist_ok=True)
    json_path = os.path.join("output", "test_gemini_output.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_output)
    print(f"\nSaved structured JSON to: {json_path}")

    # Render into visual diagram
    png_path = render_er_diagram(diagram, output_path="output/test_gemini_diagram")
    print(f"Rendered ER diagram to: {png_path}")


if __name__ == "__main__":
    run_test()