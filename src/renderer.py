import os
import graphviz
from src.models import ERDiagram


def render_er_diagram(
    diagram: ERDiagram, output_path: str = "output/er_diagram", engine: str = "dot"
) -> str:
    """Renders an ERDiagram model into a PNG image using Graphviz Chen notation."""
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    dot = graphviz.Graph(
        name="ER_Diagram",
        engine=engine,
        format="png",
        graph_attr={
            "splines": "spline",
            "overlap": "false",
            "rankdir": "LR",
            "nodesep": "0.8",
            "ranksep": "1.0",
        },
        node_attr={"fontname": "Helvetica", "fontsize": "11"},
        edge_attr={"fontname": "Helvetica", "fontsize": "10", "len": "1.5"},
    )

    for entity in diagram.entities:
        entity_node_id = f"ent_{entity.name}"
        dot.node(
            entity_node_id,
            label=entity.name,
            shape="box",
            style="bold",
            margin="0.2,0.1",
        )

        for attr in entity.attributes:
            attr_node_id = f"attr_{entity.name}_{attr.name}"
            node_kwargs = {"shape": "ellipse"}
            if attr.is_multivalued:
                node_kwargs["peripheries"] = "2"
            if attr.is_primary_key:
                dot.node(attr_node_id, label=f"<<u>{attr.name}</u>>", **node_kwargs)
            else:
                dot.node(attr_node_id, label=attr.name, **node_kwargs)

            dot.edge(entity_node_id, attr_node_id)
            if attr.composite:
                for sub_attr in attr.composite:
                    sub_node_id = f"sub_{entity.name}_{attr.name}_{sub_attr}"
                    dot.node(sub_node_id, label=sub_attr, shape="ellipse")
                    dot.edge(attr_node_id, sub_node_id)

    for idx, rel in enumerate(diagram.relationships):
        rel_node_id = f"rel_{idx}_{rel.name}"
        dot.node(rel_node_id, label=rel.name, shape="diamond", style="bold")

        card_parts = [p.strip() for p in rel.cardinality.split(":")]
        card1 = card_parts[0] if len(card_parts) > 0 else ""
        card2 = card_parts[1] if len(card_parts) > 1 else ""

        ent1_id = f"ent_{rel.entity1}"
        ent2_id = f"ent_{rel.entity2}"

        dot.edge(ent1_id, rel_node_id, label=f" {card1} ")
        dot.edge(rel_node_id, ent2_id, label=f" {card2} ")

    rendered_file = dot.render(output_path, cleanup=True)
    return rendered_file