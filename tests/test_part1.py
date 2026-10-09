import os
from src.models import ERDiagram
from src.renderer import render_er_diagram


def run_test():
    input_file = os.path.join("data", "sample_data.json")
    output_target = os.path.join("output", "test_part1_diagram")

    with open(input_file, "r", encoding="utf-8") as f:
        json_data = f.read()

    # Parse and validate schema
    diagram = ERDiagram.model_validate_json(json_data)
    print(f"Parsed {len(diagram.entities)} entities and {len(diagram.relationships)} relationships.")

    # Render image
    generated_png = render_er_diagram(diagram, output_path=output_target)
    print(f"Generated diagram successfully at: {generated_png}")


if __name__ == "__main__":
    run_test()