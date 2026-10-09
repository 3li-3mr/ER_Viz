import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models import ERDiagram, Entity, Attribute, Relationship
from src.renderer import render_er_diagram
from src.generator import generate_er_diagram_from_text


def test_1_official_schema():
    print("\n[TEST 1] Verifying Part 1 against official assignment schema...")
    sample_path = os.path.join("data", "sample_data.json")
    if not os.path.exists(sample_path):
        sample_path = os.path.join("data", "sample_input.json")

    assert os.path.exists(sample_path), f"Sample file not found at {sample_path}"

    with open(sample_path, "r", encoding="utf-8") as f:
        data = f.read()

    diagram = ERDiagram.model_validate_json(data)
    out_img = render_er_diagram(diagram, output_path="output/verify_test1_official")
    assert os.path.exists(out_img), f"Output image not created: {out_img}"
    print(f"  -> SUCCESS: Official schema rendered to {out_img}")


def test_2_collision_and_cardinality_edge_cases():
    print("\n[TEST 2] Verifying edge cases (duplicate attribute names & cardinalities)...")
    edge_case_diagram = ERDiagram(
        entities=[
            Entity(
                name="Student",
                attributes=[
                    Attribute(name="ID", isPrimaryKey=True),
                    Attribute(name="Name", composite=["First", "Last"]),
                    Attribute(name="Email", isMultiValued=True),
                ],
            ),
            Entity(
                name="Club",
                attributes=[
                    Attribute(name="ID", isPrimaryKey=True),
                    Attribute(name="Name"),  # Shared attribute name with Student
                ],
            ),
            Entity(
                name="Locker",
                attributes=[
                    Attribute(name="LockerNumber", isPrimaryKey=True),
                ],
            ),
        ],
        relationships=[
            Relationship(
                name="Member_Of", entity1="Student", entity2="Club", cardinality="M:N"
            ),
            Relationship(
                name="Assigned_To",
                entity1="Student",
                entity2="Locker",
                cardinality="1:1",
            ),
            # New relationship forming a closed loop (triangle topology)
            Relationship(
                name="Stores_Gear",
                entity1="Club",
                entity2="Locker",
                cardinality="1:N",
            ),
        ],
    )

    out_img = render_er_diagram(
        edge_case_diagram, output_path="output/verify_test2_edge_cases"
    )
    assert os.path.exists(out_img), f"Output image not created: {out_img}"
    print(f"  -> SUCCESS: Edge case diagram rendered to {out_img}")


def test_3_gemini_pipeline():
    print("\n[TEST 3] Verifying Part 2 end-to-end Gemini extraction...")
    prompt = (
        "Design a library system. A Member has a member_id (primary key), "
        "a full_name consisting of first_name and last_name, and multiple phone_numbers. "
        "A Book has an isbn (primary key) and a title. "
        "A Member borrows Books (cardinality 1:N)."
    )

    diagram = generate_er_diagram_from_text(prompt)
    assert len(diagram.entities) >= 2, "Failed to extract entities."
    assert len(diagram.relationships) >= 1, "Failed to extract relationships."

    # Verify JSON serializability
    json_str = diagram.model_dump_json(indent=2, by_alias=True)
    parsed = json.loads(json_str)
    assert "entities" in parsed and "relationships" in parsed

    # Save and render
    json_path = "output/verify_test3_ai.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_str)

    out_img = render_er_diagram(diagram, output_path="output/verify_test3_ai")
    assert os.path.exists(out_img), f"Output image not created: {out_img}"
    print(f"  -> SUCCESS: AI pipeline created {json_path} and {out_img}")


def main():
    os.makedirs("output", exist_ok=True)
    try:
        test_1_official_schema()
        test_2_collision_and_cardinality_edge_cases()
        test_3_gemini_pipeline()
        print("\n==========================================")
        print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY")
        print("==========================================")
    except AssertionError as err:
        print(f"\n[FAIL] Assertion failed: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"\n[ERROR] An unexpected error occurred: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()