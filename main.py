import argparse
import os
import sys
from src.generator import generate_er_diagram_from_text
from src.models import ERDiagram
from src.renderer import render_er_diagram


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI-Powered ER Diagram Generator (CSE-471 Lab 1)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-t",
        "--text-file",
        type=str,
        help="Path to a text file containing the natural language system description.",
    )
    group.add_argument(
        "-j",
        "--json-file",
        type=str,
        help="Path to an existing JSON file conforming to the ER schema.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="output/er_diagram",
        help="Output image path prefix without extension (default: 'output/er_diagram').",
    )
    parser.add_argument(
        "--engine",
        type=str,
        default="dot",
        choices=["dot", "neato", "fdp", "circo"],
        help="Graphviz layout engine (default: 'dot').",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.json_file:
        if not os.path.exists(args.json_file):
            print(f"Error: JSON file not found at '{args.json_file}'", file=sys.stderr)
            sys.exit(1)

        print(f"Loading structured JSON from '{args.json_file}'...")
        with open(args.json_file, "r", encoding="utf-8") as f:
            json_str = f.read()

        diagram = ERDiagram.model_validate_json(json_str)

    elif args.text_file:
        if not os.path.exists(args.text_file):
            print(f"Error: Text file not found at '{args.text_file}'", file=sys.stderr)
            sys.exit(1)

        print(f"Reading requirement text from '{args.text_file}'...")
        with open(args.text_file, "r", encoding="utf-8") as f:
            prompt_text = f.read()

        print("Requesting ER model extraction from Gemini API...")
        diagram = generate_er_diagram_from_text(prompt_text)

        out_dir = os.path.dirname(args.output) or "output"
        os.makedirs(out_dir, exist_ok=True)
        base_name = os.path.basename(args.output)
        json_out_path = os.path.join(out_dir, f"{base_name}.json")

        with open(json_out_path, "w", encoding="utf-8") as f:
            f.write(diagram.model_dump_json(indent=2, by_alias=True))
        print(f"Intermediate JSON saved to '{json_out_path}'")

    print(f"Rendering ER diagram using Graphviz (engine='{args.engine}')...")
    output_png = render_er_diagram(
        diagram, output_path=args.output, engine=args.engine
    )
    print(f"Diagram successfully generated at: '{output_png}'")


if __name__ == "__main__":
    main()