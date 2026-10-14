import os
import graphviz
from src.models import ERDiagram


def render_er_diagram(
    diagram: ERDiagram, output_path: str = "output/er_diagram", engine: str = "dot"
) -> str:
    """
    Renders an ERDiagram model into a clean PNG using Chen ER notation.
    Uses Graphviz 'dot' with invisible clusters to guarantee obstacle avoidance
    and prevent relationship edges from slicing through attribute ovals.
    """
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    dot = graphviz.Graph(
        name="ER_Diagram",
        engine="dot",  # 'dot' guarantees geometric obstacle avoidance
        format="png",
        graph_attr={
            "splines": "spline",       # Smooth curves routing around node obstacles
            "rankdir": "LR",           # Left-to-right academic Chen ER layout
            "nodesep": "0.9",          # Spacing between nodes on the same rank
            "ranksep": "1.3",          # Spacing between ranks
            "compound": "true",
            "overlap": "false",
        },
        node_attr={"fontname": "Helvetica", "fontsize": "10"},
        edge_attr={"fontname": "Helvetica", "fontsize": "9"},
    )

    # 1. Enclose each Entity and its Attributes in an Invisible Cluster
    # This quarantines attributes so relationship edges cannot pass through them.
    for entity in diagram.entities:
        cluster_name = f"cluster_{entity.name}"
        with dot.subgraph(name=cluster_name) as sub:
            sub.attr(style="invis")

            entity_node_id = f"ent_{entity.name}"
            entity_kwargs = {"shape": "box", "style": "bold", "margin": "0.15,0.08"}
            if entity.is_weak:
                entity_kwargs["peripheries"] = "2"

            sub.node(entity_node_id, label=entity.name, **entity_kwargs)

            for attr in entity.attributes:
                attr_node_id = f"attr_{entity.name}_{attr.name}"
                node_kwargs = {"shape": "ellipse", "margin": "0.08,0.04"}

                if attr.is_multivalued:
                    node_kwargs["peripheries"] = "2"

                if attr.is_derived:
                    node_kwargs["style"] = "dashed"

                if attr.is_primary_key:
                    label_str = f"<<u>{attr.name}</u>>"
                elif attr.is_partial_key:
                    label_str = (
                        f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">'
                        f'<TR><TD BORDER="1" SIDES="B" STYLE="DASHED">{attr.name}</TD></TR>'
                        f'</TABLE>>'
                    )
                else:
                    label_str = attr.name

                sub.node(attr_node_id, label=label_str, **node_kwargs)
                sub.edge(entity_node_id, attr_node_id)

    for idx, rel in enumerate(diagram.relationships):
        rel_node_id = f"rel_{idx}_{rel.name}"
        rel_kwargs = {"shape": "diamond", "style": "bold", "margin": "0.15,0.08"}
        if rel.is_identifying:
            rel_kwargs["peripheries"] = "2"

        dot.node(rel_node_id, label=rel.name, **rel_kwargs)

        for p_idx, part in enumerate(rel.participants):
            ent_node_id = f"ent_{part.entity}"
            edge_color = "black:black" if part.participation.lower() == "total" else "black"
            card_label = f" {part.cardinality} "

            if p_idx == 0:
                dot.edge(
                    ent_node_id,
                    rel_node_id,
                    label=card_label,
                    color=edge_color,
                )
            else:
                dot.edge(
                    rel_node_id,
                    ent_node_id,
                    label=card_label,
                    color=edge_color,
                )

    return dot.render(output_path, cleanup=True)