from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Attribute(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    is_primary_key: bool = Field(default=False, alias="isPrimaryKey")
    is_multivalued: bool = Field(default=False, alias="isMultiValued")
    composite: Optional[List[str]] = None


class Entity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    is_weak: bool = Field(default=False, alias="isWeak")
    attributes: List[Attribute] = Field(default_factory=list)


class Participant(BaseModel):
    """Represents an entity's participation in an n-ary relationship."""

    model_config = ConfigDict(populate_by_name=True)
    entity: str
    cardinality: str = "1"
    participation: str = "partial"


class Relationship(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    is_identifying: bool = Field(default=False, alias="isIdentifying")
    participants: List[Participant] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_binary_and_nary(cls, data: Any) -> Any:
        """
        Maintains backwards compatibility with Listing 1 (entity1, entity2, cardinality)
        while accepting modern n-ary structures.
        """
        if isinstance(data, dict):
            # If the legacy binary format is passed:
            if "entity1" in data and "entity2" in data:
                card = data.get("cardinality", "1:1")
                card_parts = [p.strip() for p in card.split(":")]
                c1 = card_parts[0] if len(card_parts) > 0 else "1"
                c2 = card_parts[1] if len(card_parts) > 1 else "1"

                p1 = data.get("entity1Participation", "partial")
                p2 = data.get("entity2Participation", "partial")

                data["participants"] = [
                    {"entity": data["entity1"], "cardinality": c1, "participation": p1},
                    {"entity": data["entity2"], "cardinality": c2, "participation": p2},
                ]
        return data


class ERDiagram(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)