from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class Attribute(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    is_primary_key: bool = Field(default=False, alias="isPrimaryKey")
    is_multivalued: bool = Field(default=False, alias="isMultiValued")
    composite: Optional[List[str]] = None


class Entity(BaseModel):
    name: str
    attributes: List[Attribute] = Field(default_factory=list)


class Relationship(BaseModel):
    name: str
    entity1: str
    entity2: str
    cardinality: str 


class ERDiagram(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)